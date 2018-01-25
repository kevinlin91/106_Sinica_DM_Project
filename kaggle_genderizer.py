import pandas as pd
import gender_guesser.detector as gender
d=gender.Detector(case_sensitive=False)
df1=pd.read_csv("C:\Users\GADO\Documents\pythonExcercise\ss.csv")
#df1.set_index('DisplayName')

name_list=[]
gender_list=[]

#iterate each name and detect the gender [Male,Female,mostly_male,mostly_female or unknown]
# indicates the first 50 users in the data frame
for i in range (0,50,1):
  x=df1.ix[i,0]
  name_list.insert(i,x)
  gender_list.insert(i,(d.get_gender(x)))
  
#create new data frame and then put the two lists side by side
new_dataframe=pd.DataFrame()
new_dataframe['name']=name_list
new_dataframe['gender']=gender_list

#dump the new_dataframe as csv file
new_dataframe.to_csv('C:\Users\GADO\Documents\pythonExcercise\genderizer_result.csv.csv')
#
print new_dataframe
