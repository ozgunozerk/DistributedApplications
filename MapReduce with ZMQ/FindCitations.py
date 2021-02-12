from MapReduce import MapReduce

class FindCitations(MapReduce):
    def Map(self, parts):
        length = len(parts)

        my_dict={}

        for i in range(length):
            #print("key: ",test1[i][1])
            if parts[i][1] in my_dict:
                #print("key exists: ", parts[i][1])
                my_dict[parts[i][1]] += 1
            else:
                #print("key doesnt exists: ",parts[i][1])
                my_dict[parts[i][1]] = 1
        return my_dict


    def Reduce(self, kvs):
        if kvs is None:
            return None
            
        new_dict={}
        for i in range(len(kvs)):
            # kvs = [{'3': 1, '7': 1}, {'3': 1, '2': 1, '7': 1}, {'3': 2, '1': 1}, {'5': 1, '2': 1}]
            for key, value in kvs[i].items():
              if key in new_dict:
                new_dict[key] += value
              else:
                new_dict[key] =  value

                    
        return new_dict
            


