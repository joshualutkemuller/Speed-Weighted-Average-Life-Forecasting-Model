import pandas as pd
import timeit
import time

def DataFrame_Looper(security_list,yield_list,speed_list,term_list):

    start_time = time.time()

    df = pd.DataFrame(columns = ['Security','Yield','Speed','Term'])


    counter=0
    for i in range(len(security_list)):

        security_value = security_list[i]

        for i in range(len(yield_list)):

            yield_value = yield_list[i]


            for i in range(len(speed_list)):
                
                speed_value = speed_list[i]

                for i in range(len(term_list)):

                    term_value = term_list[i]

                    df.loc[counter] = [security_value
                                       ,yield_value
                                       ,speed_value
                                       ,term_value]
                    
                    counter += 1


    time_elapse = time.time() - start_time
    print(f'The dataframe builder code took {time_elapse} seconds to complete')

    #return dataframe
    return df


df = DataFrame_Looper(security_list=security_list,
                 yield_list=yield_list,
                 speed_list=speed_list,
                 term_list=term_list)

#print(timeit.repeat(stmt='DataFrame_Looper(security_list=security_list,yield_list=yield_list,speed_list=speed_list,term_list=term_list)',setup='from __main__ import DataFrame_Looper',repeat=10,number=1))

        