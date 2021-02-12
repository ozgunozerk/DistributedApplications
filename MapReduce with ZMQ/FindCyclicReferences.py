from MapReduce import MapReduce
import collections

class FindCyclic(MapReduce):
    def Map(self, parts):
        length = len(parts)
        
        my_dict={}        
        
        for i in range(length):
            if parts[i][0] in my_dict:
                #print("key exists: ", parts[i][0])
                my_dict[parts[i][0]].append(parts[i][1])
            else:
                #print("key doesnt exists: ",parts[i][0])
                my_dict[parts[i][0]] = [parts[i][1]]

        return my_dict


    def Reduce(self, kvs):
        if kvs is None:
            return None

        super_dict = collections.defaultdict(set)
        for d in kvs:
            for k, v in d.items():  # d.items() in Python 3+
                for ele in v:
                    super_dict[k].add(ele)


        new_dict={}
        temp_tup = (0,0)
        for key in list(super_dict):
            for value in super_dict[key]:
                if int(key) in super_dict[str(value)]:
                    if int(key) < value:
                        temp_tup = (int(key),value)
                        new_dict[str(temp_tup)] = 1
                        break
                    else:
                        temp_tup = (value,int(key))
                        new_dict[str(temp_tup)] = 1
                        break

        return new_dict
    

