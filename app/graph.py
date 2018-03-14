import json
from graph_tool import Graph, topology
import itertools
from itertools import groupby
import pickle
import graph_tool
from app.models import *
from app.settings import *
import copy

class graphtool():

    def get_edges(self):
        self.edges = []
        for dev in Device.objects:
            port = dev['ports']
            for port in dev['ports']:
                if not port['acc']:
                    self.edges.append([int(port['dev']), int(dev['devid'])])
        for edge in self.edges:
            if edge[::-1] in self.edges:
                self.edges.remove(edge)            

    def create_graph(self):
        self.get_edges()
        self.g = Graph(directed=False)
        self.g.add_edge_list(self.edges)

    def load_graph(self):
        self.g = pickle.loads(System.objects.first().graph.read())


    def shortestpath(self, source, dest):
        if source == dest:
            return ('нужны разные пипишники')
        #ip to id
        source = Device.objects(uri=source)
        dest = Device.objects(uri=dest)
        if len(source) >0 and len(dest) >0:
            source = self.g.vertex(source[0].devid)
            dest = self.g.vertex(dest[0].devid)
            result = graph_tool.topology.shortest_path(self.g, source, dest)
            path = [self.g.vertex_index[x] for x in result[0]]
            filteredge = self.g.new_edge_property('bool')
            filteredge[result[1][0]] = True
            self.g.set_edge_filter(filteredge, inverted=True)
            result = graph_tool.topology.shortest_path(self.g, source, dest)
            second_path = [self.g.vertex_index[x] for x in result[0]]
            self.g.clear_filters()      
            another_paths = []
            all_shortest = graph_tool.topology.all_shortest_paths(self.g, source, dest)
            for i in all_shortest:
                another_paths.append([self.g.vertex_index[j] for j in i])

            self.all_paths = [path] + [second_path] + another_paths
            self.all_paths = [tuple(t) for t in self.all_paths]
            self.all_paths = [t for t in self.all_paths if len(t) > 0]
            self.all_paths = list(set(self.all_paths))
            self.all_paths = [list(t) for t in self.all_paths]

            dev_from_stp = []
            count = 0
            for path in self.all_paths:
                for dev in path:
                    dev =  Device.objects(devid=dev).first().uri  
                    if Stpdomins.objects(devices__=dev):
                        count += 1
                        [dev_from_stp.append(x) for x  in Stpdomins.objects(devices__=dev).first().devices if x not in dev_from_stp]
            
            if len(dev_from_stp) > 0 and count >1:
                print('stp domains')
                filtevertex = self.g.new_vertex_property('bool')
                for x in dev_from_stp:
                    filtevertex[self.g.vertex(Device.objects(uri=x).first().devid)] = True
                self.g.set_vertex_filter(filtevertex)

                source = self.g.vertex(Device.objects(uri=dev_from_stp[0]).first().devid)
                dest = self.g.vertex(Device.objects(uri=dev_from_stp[-1]).first().devid)
                result = graph_tool.topology.all_paths(self.g, source, dest)
                for x in result:
                    self.all_paths.append( [int(self.g.vertex(i)) for i in x] )
                self.g.clear_filters()
                self.all_paths.sort() 
                self.all_paths = list(self.all_paths for self.all_paths,_ in itertools.groupby(self.all_paths))
                self.all_paths = [path for path in  self.all_paths if len(path)>0]

        return self.all_paths        

        





    def fancy_shortest(self):
        self.fancy_paths = []
        for path in self.all_paths:
            fancy = []
            for i in path:
                d = Device.objects(devid=i).first()
                if d.devtype not in passive:
                    fancy.append([d.uri, d.addr, dev_type_dict[d.devtype]])
            self.fancy_paths.append(fancy)
        return self.fancy_paths    

            

    def paths_ports(self):
        output = []       
        for path in self.all_paths:         
                for i, j in zip(path, path[1:]):

                    dev = Device.objects(devid=i).first()
                    if dev.devtype in  supported:
                        ports = [x['num'] for x in dev.ports if x['dev'] == j]
                        if len(ports) == 0:
                            ports = 0
                        else:
                            ports = ports[0]      
                        output.append([dev.uri, dev.devtype, ports])
                       
                    dev = Device.objects(devid=j).first()
                    if dev.devtype in  supported: 
                        ports = [x['num'] for x in dev.ports if x['dev'] == i]
                        if len(ports) == 0:
                            ports = 0
                        else:
                            ports = ports[0] 
                        output.append([dev.uri, dev.devtype, ports])
      
        g_fancy_output = dict()               
        g_output = dict()
        for key, group in groupby(output , lambda x: x[0]):
            ports = []
            for i in group:
                ports.append(i[2])
            if key in g_output:
                # print (g_output[key]['ports'], ports)
                g_output[key]['ports'] = g_output[key]['ports'] + ports
            else:
                g_output[key] = {'type':i[1], 'ports':ports}

        for key in g_output:
            g_output[key]['ports'] = list(set(g_output[key]['ports']))

        g_fancy_output = copy.deepcopy(g_output)
        for i in g_fancy_output:
            g_fancy_output[i]['type'] = dev_type_dict[g_fancy_output[i]['type']]
        return g_fancy_output, g_output


# if __name__ == "__main__":

#     worker = graphtool()
#     worker.create_graph()
#     worker.shortespath('10.157.0.54', '10.157.0.150')
#     worker.paths_ports()



