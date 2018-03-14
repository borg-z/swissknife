from app import app
from flask import render_template, url_for, session, redirect, make_response, send_file
from app.models import *
from app.graph import graphtool
from flask import jsonify, request, flash
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import SelectField, SelectMultipleField, SubmitField
import ast
from app.settings import acc
from jinja2 import Environment, PackageLoader, meta, BaseLoader
from app.settings import dev_type_dict
from app.tasks import *
import sys
from datetime import datetime, timedelta
import uuid
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user,  current_user, AnonymousUserMixin
from jinja2 import Environment
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
from shutil import copyfile
import re

limiter = Limiter(
    app,
    key_func=get_remote_address)

rq.init_app(app)
graph = graphtool()
db.init_app(app)

# update_graph()
app.secret_key = 'brahmaputraflyhighelse'
update_graph.cron('0 */3 * * *', 'update-graph and data')


class NonValidatingSelect(SelectField):
    def pre_validate(self, form):
        pass


class User():
    """
    Class for flask login.  
    More in https://flask-login.readthedocs.io/en/latest/
    """

    def __init__(self, username):
        self.username = username

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username


@login_manager.user_loader
def load_user(username):
    """
    Flask login helper.
    More in https://flask-login.readthedocs.io/en/latest/
    """
    u = DBUser.objects(user=username).first()
    if not u:
        return None
    return User(str(u.user))


class devuriform(FlaskForm):
    """
    Form for /paths used in Stage1 for select2
    """
    src = NonValidatingSelect("Source", validators=[DataRequired()],
                              choices=[],
                              render_kw={})
    dst = NonValidatingSelect("Destination", validators=[DataRequired()],
                              choices=[],
                              render_kw={})
    submit = SubmitField('Calculate')


@app.route('/checkmac', methods=['GET', 'POST'])
@login_required
def checkmac():
    """
    Function for check stage from /paths.
    """
    if request.method == 'POST':
        """
        Example: {"cisco":"91.244.255.248","to_check":{"10.3.5.3":{"ports":[0],"type":"46"},"10.3.5.8":{"ports":[25],"type":"23"}},"vlan":"777"}
        """
        check = ast.literal_eval(request.form['check'])
        vlan = check['vlan'].strip()
        cisco = check['cisco'].strip()
        to_check = check['to_check']
        cisco_check_vlan.queue(cisco, vlan, 'add')
        result = []
        for ip in to_check:
            devtype = to_check[ip]['type']
            if devtype in supported_switches:  # configured in settings.py
                job = get_mac_vlan.queue(devtype, ip, vlan)  # job in tasks.py
                result.append({'job': job.id, 'dev': ip})
        cisco_check_vlan(cisco, vlan, 'del')
        return jsonify(result)  # return json result


@app.route('/devtemplates/', methods=['GET', 'POST'])
@login_required
def devtempltes():
    """
    Main page of template module.  Just displays template list.
    """
    if request.args.get('delete'):  # delete template
        Templates.objects(name=request.args.get('delete')).first().delete()
        return redirect('/devtemplates')
    templatelist = [x for x in Templates.objects()]
    return render_template('devtemplates.html', templatelist=templatelist)


@app.route('/utilite1/', methods=['GET', 'POST'])
@login_required
def utilite():
    """
    Static page with some js code
    """
    return render_template('utilite1.html')


@app.route('/devtemplate/<t_id>', methods=['GET', 'POST'])
@login_required
def devtemplte(t_id):
    """
    View for template.  Create new, edit and delete.
    """
    templatelist = [x for x in Templates.objects()]
    # Creating new template
    if t_id == 'new':
        # just render page
        if request.method == 'GET':
            return render_template('devtemplatenew.html',  templatelist=templatelist)
        # get params from request and write new template to DB
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            template = request.form['template']
            try:
                # checks that template is valid and has jinja2 variables
                env = Environment()
                parse = env.parse(template)
                variables = list(meta.find_undeclared_variables(parse))
                variables = [{'name': x, 'description': None}
                             for x in variables]
                if len(variables) == 0:
                    flash('Invalid template provided', 'error')
                    return redirect('/devtemplate/new')
            except:
                flash('Invalid template provided', 'error')
                return redirect('/devtemplate/new')
            Templates.objects(name=name).modify(
                upsert=True, new=True, description=description, template=template, variables=variables)
            return redirect('/devtemplates')
    else:
        # If template is exist
        if request.method == 'POST':
            if request.form.get('editvariable'):
                # edit variables.
                variable = request.form['editvariable']
                #Example: {"name":"NETMASK","value":"255.255.255.0"}
                variable = ast.literal_eval(variable)
                variables = Templates.objects(name=t_id).first().variables
                """
                [{'description': '34534534',
                'name': 'ports',
                'value': "[{'a':1,'b':2},{'a':3,'b':4}]"}]
                """
                variables = [dict(
                    x) for x in variables]  # from mongoengine.base.datastructures.BaseList to list of dict
                for i in variables:
                    if i['name'] == variable['name']:
                        if 'description' in variable.keys():
                            # update description
                            i['description'] = variable['description']
                            Templates.objects(name=t_id).modify(
                                upsert=True, new=True, variables=variables)
                            return jsonify(variable['description'])
                        if 'value' in variable.keys():
                            # update default value
                            i['value'] = " ".join(
                                variable['value'].split()).replace(' ', '')
                            Templates.objects(name=t_id).modify(
                                upsert=True, new=True, variables=variables)
                            return jsonify(variable['value'])
            else:
                # edit exist template
                name = request.form['name']
                description = request.form['description']
                template = request.form['template']
                if t_id != name:
                    # rename
                    Templates.objects(name=t_id).modify(name=name)
                try:
                    env = Environment()
                    parse = env.parse(template)

                    # get variables from request
                    getvariables = list(meta.find_undeclared_variables(parse))
                    dbvariables = Templates.objects(name=name).first(
                    ).variables  # get variables from database
                    """
                    Diff of variables from the database and the request. If exist just modify.
                    When we edit template variables are parsed from template. And this variables has not description and default values.
                    To prevent existing variables with description and values from being overwritten, we use this step.
                    If variable exist in database and in request, we copy description and values from old to new.
                    """
                    for x in dbvariables:
                        if x['name'] in getvariables:
                            variables.append(x)
                            getvariables.remove(x['name'])
                    for x in getvariables:
                        variables.append({'name': x, 'description': None})
                    if len(variables) == 0:
                        # If there are no variables in the template
                        flash('Invalid template provided', 'error')
                        return redirect('/devtemplate/{}'.format(t_id))
                    else:
                        Templates.objects(name=name).modify(
                            upsert=True, new=True, description=description, template=template, variables=variables)
                        return redirect('/devtemplates')
                except:
                    flash('Invalid template provided', 'error')
                    return redirect('/devtemplate/new')

        if request.method == 'GET':
            """
            Just render template
            """
            template = Templates.objects(name=t_id).first()
            return render_template('devtemplate.html', templatelist=templatelist,  template=template)


@app.route('/devtemplategen', methods=['GET', 'POST'])
@login_required
def devtemplategen():
    """
    Generate config from template.
    """
    templatelist = [x for x in Templates.objects()]
    if request.method == 'GET':
        if request.args.get('save'):
            # save config as file
            filename = 'configs/'+request.args.get('save')
            return send_file(filename, as_attachment=True)
        if request.args.get('tftp'):
            # copy config to tftp server
            filename = request.args.get('tftp')
            src = 'app/configs/'+filename
            copyfile(src, '/var/tftpboot/{}'.format(filename))
            flash('Configure ISCOM2128')
            flash("download boot tftp 10.3.2.83 2128boot")
            flash("download system-boot tftp 10.3.2.83 2128firmware")
            flash(
                "download remote-startup-config tftp 10.3.2.83 {} startup-config".format(filename))
            flash("Configure Mikrotik:")
            flash("""/system script  add name=import_config owner=admin policy=ftp,reboot,read,write,policy,test,password,sniff,sensitive,romon source="/tool fetch mode=tftp address=tools.loc src-path={} dst-path=config\\r\\
                        \\n:delay 3\\r\\
                        \\n/tool fetch mode=tftp address=tools.loc src-path=mconfig.rcs dst-path=mconfig.rcs\\r\\
                        \\n:delay 3\\r\\ "
                         """.format(filename))
            flash("/system script run import_config")
            return redirect('/devtemplategen')
        return render_template('devtemplategen.html', templatelist=templatelist)
    if request.method == 'POST':
        # Get variables from template
        if request.form.get('getvaribles'):
            template = request.form.get('getvaribles')
            variables = Templates.objects(name=template).first().variables
            return jsonify(variables)
        if request.form.get('copyssh'):
            # Copy generated template with scp
            r = ast.literal_eval(request.form.get('copyssh'))
            # [username,  password, filename, sshpath]
            ip = r[-1].split(':')[0]
            dst = r[-1].split(':')[1]
            job = scp_copy.queue(ip, r[0],  r[1], r[2], dst)
            return jsonify(job.id)
        else:
            # get variables and they values and convert to dict
            # Request example "name=Nanobeam+M5AC+Station&VLAN=123&SSID=ubnt&NETMASK=255.255.255.0&GATEWAY=10.111.0.1&IP=10.111.0.2"
            values = request.form.to_dict(flat=False)
            for i in values:
                # Convert to python object if possible. For example value is '[1,2,3]'.
                values[i] = values[i][0]
                try:
                    values[i] = ast.literal_eval(values[i])
                except:
                    # If value is not python object just do nothing
                    pass
            name = values['name']
            # Removes 'name' from values. All other values are used as variables
            del values['name']
            rtemplate = Environment(loader=BaseLoader()).from_string(
                Templates.objects(name=name).first().template)
            response = str(rtemplate.render(**values))
            # For example: Nanobeam_M5AC_Station_aeb79e48-2596-4aec-a49c-6e0ea75d1dd5.txt
            filename = " ".join(name.split()).replace(
                ' ', '_')+'_'+str(uuid.uuid4())+'.txt'
            with open('app/configs/'+filename, 'w') as f:
                f.write(response)  # save file
            return render_template('devtemplategen.html', templatelist=templatelist, filename=filename)


@app.route('/dev_uri', methods=['GET', 'POST'])
@login_required
def device_uris():
    """
    Getting devices from database for select2.
    """
    text = request.args.get('q')
    count = 0
    result = []
    query = Device.objects(uri__contains=text)
    if len(query) > 0:
        for i in query:
            result.append({'id': i.devid, 'text': i.uri})
    else:
        result = [{'id': 0, 'text': 'Not found'}]
    result.append({"more": False})
    return jsonify(result)


@app.route('/dev_uri_access', methods=['GET', 'POST'])
@login_required
def dev_uri_access():
    text = request.args.get('q')
    count = 0
    result = []
    query = Device.objects(devtype__in=access_switches, uri__contains=text)
    if len(query) > 0:
        for i in query:
            result.append({'id': i.devid, 'text': i.uri})
    else:
        result = [{'id': 0, 'text': 'Not found'}]
    result.append({"more": False})
    return jsonify(result)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_password_hash(DBUser.objects(user=username).first().password, password):
            user = User(str(DBUser.objects(user=username).first().user))
            login_user(user)
            return redirect('/')
        else:
            flash('Username or password incorrect')
            return redirect('/login')
    else:
        return render_template("login.html")


@limiter.limit("1 per minute", get_remote_address)
@app.route('/exterminatus_work', methods=['POST'])
@login_required
def mgmdestroy_work():
    job = destroyer.queue(acc)
    return jsonify(job.id)


@app.errorhandler(429)
def ratelimit_handler(e):
    return make_response(
        jsonify(error="ratelimit exceeded %s" % e.description), 200
    )


@app.route('/exterminatus', methods=['GET'])
@login_required
def mgmdestroy():
    return render_template('mgmdestroyer.html')


@app.route('/create')
@login_required
def crate_graph():
    """
    Loading graph from database.
    """
    graph.load_graph()
    return ' '.join(str(graph.g).strip('<>').split()[0:9])


@app.route('/shortest', methods=['POST', 'GET'])
@login_required
def shortest():
    """
    Get shortest path. Returns raw data and 'fancy' with device type and address.
    [[[["10.3.5.13",Street 15","Switch a"],["10.3.5.12","Street 15","ISCOM2128EA-MA"]]],[[5658,5651]]]
    """
    src = request.args.get('src')
    dst = request.args.get('dst')
    print(src, dst)
    if graph:
        graph.shortestpath(src, dst)
        return jsonify(graph.fancy_shortest(), graph.all_paths)


@app.route('/withports', methods=['POST', 'GET'])
@login_required
def withports():
    """
    Return path with ports.
    Example request: items=[0] shortest=[[5658,5651]]
    """
    checkboxes = ast.literal_eval(request.args.get('items'))
    choised_paths = ast.literal_eval(request.args.get('shortest'))
    all_paths = []
    for i in checkboxes:
        all_paths.append(choised_paths[int(i)])
    graph.all_paths = all_paths
    return jsonify(graph.paths_ports())


@limiter.limit("5 per minute", get_remote_address)
@login_required
@app.route('/write')
def write():
    vlan = request.args.get('vlan')
    try:
        vlans = ast.literal_eval(vlan)
    except:
        pass
    if not isinstance(vlans, list):
        vlans = [vlans]
    write_dict = ast.literal_eval(request.args.get('write_dict'))
    result = []
    for dev in write_dict:
        job = write_trunk.queue(write_dict[dev], dev, vlans)
        result.append({'job': job.id, 'dev': dev})
    return jsonify(result)


@app.route('/status/<job_id>')
@login_required
def job_status(job_id):
    """
    Get flask_rq2 job status
    """
    app.logger.warn(job_id)
    q = rq.get_queue('default')
    job = q.fetch_job(job_id)
    if job is None:
        response = {'status': 'unknown'}
    else:
        if job.is_failed:
            response = {'status': 'failed'}
        else:
            response = {
                'status': job.get_status(),
                'result': job.result,
            }
    return jsonify(response)


@limiter.limit("3 per hour", get_remote_address)
@app.route('/systemupdate', methods=['GET', 'POST'])
@login_required

def systemupdate():
    """
    Update graph. Creates task in flask_rq2. This task get data from billing and creates graph.
    """
    job = update_graph.queue()
    return jsonify(job.id)


@app.route('/stpdomains', methods=['GET', 'POST'])
@login_required
def stpdomains():
    """
    STP domains module. This module is necessary for difficult stp topology (not simple ring.)
    You must adding all devices thath are in STP domain. Then if you would create path from one devices that is in this ring, path would calculate throught all ring.
    You can delete, edit and create.
    """
    domainslist = dict()
    domains = [x.domain for x in Stpdomins.objects()]
    for domain in domains:
        domainslist[domain] = Stpdomins.objects(domain=domain).first().devices

    if request.args.get('create'):
        data = ast.literal_eval(request.args.get('create'))
        if len([x for x in data if Stpdomins.objects(devices__=x)]) > 0:
            return jsonify({'error': 'some device allready exist in another domain'})
        domainid = str(uuid.uuid4())
        Stpdomins.objects(domain=domainid).modify(
            upsert=True, new=True, devices=data)
        return jsonify({domainid: data})

    if request.args.get('edit'):
        data = ast.literal_eval(request.args.get('edit'))
        Stpdomins.objects(domain=data[0]).modify(
            upsert=True, new=True, devices=data[1])
        response = Stpdomins.objects(domain=data[0]).first().devices
        return jsonify(response)

    if request.args.get('delete'):
        data = request.args.get('delete')
        Stpdomins.objects(domain=data).delete()
        return jsonify(data)

    else:
        return render_template('stpdomains.html', domainslist=domainslist)


@app.route('/access', methods=['GET', 'POST'])
@login_required
def access():
    """
    Write access vlan to witch port.
    """
    if request.method == 'POST':
        if request.form.get('emptyports'):
            device = request.form.get('emptyports')
            deviceid = Device.objects(uri=device).first().devid
            getdevice = get()
            devicedata = getdevice.getsingledevice(deviceid)
            busyports = [x['Number'] for x in devicedata['Ports']]
            emptyports = [x for x in range(1, 29) if x not in busyports]
            devtype = Device.objects(uri=device).first().devtype
            portstatus = get_ports_status(device, devtype)
            portstatus = [[x, portstatus[str(x)]] for x in emptyports]
            return jsonify(portstatus)
        if request.form.get('write'):
            data = ast.literal_eval(request.form.get('write'))
            data['type'] = Device.objects(uri=data['ip']).first().devtype
            job = write_access.queue(data)
            return jsonify(job.id)

    else:
        return render_template('access.html')


@app.route('/updategraph')
@login_required
def system():
    """
    Just render page
    """
    siteupdate = System.objects.first().siteupdate.strftime("%Y-%m-%d %H:%M:%S")
    graphupdate = System.objects.first().graphupdate.strftime("%Y-%m-%d %H:%M:%S")
    if request.args.get('status'):
        return jsonify(siteupdate, graphupdate)
    elif request.method == 'POST':
        job = update_graph.queue()
        return jsonify(job.id)
    return render_template('updategraph.html', siteupdate=siteupdate, graphupdate=graphupdate)


@app.route('/paths', methods=['GET', 'POST'])
@login_required
def paths():
    """
    Just render page
    """
    form = devuriform()
    return render_template("paths.html",  form=form)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    """
    Just render page
    """
    return render_template('index.html')
