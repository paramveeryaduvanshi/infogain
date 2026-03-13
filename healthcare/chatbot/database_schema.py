# Database_schema = {'Dataset1': ['Patient_Number', 'Blood_Pressure_Abnormality', 'Level_of_Hemoglobin',
#                                 'Genetic_Pedigree_Coefficient', 'Age', 'BMI', 'Sex', 'Pregnancy',
#                                 'Smoking', 'salt_content_in_the_diet', 'alcohol_consumption_per_day',
#                                 'Level_of_Stress', 'Chronic_kidney_disease', 'Adrenal_and_thyroid_disorders'],
#                                 'Dataset2': ['Patient_Number', 'Day_Number', 'Physical_activity']}


metadata_structure = {
    'Dataset1': {
        'Patient_Number': int, #eg. 1,2,3...100
        'Blood_Pressure_Abnormality': float, # between 0 to 1,
        'Level_of_Hemoglobin': float,
        'Genetic_Pedigree_Coefficient': float, # between 0 to 1,
        'Age': int,
        'BMI': int,
        'Sex': str, #Male or Female
        'Pregnancy': str, #Yes or No
        'Smoking': str, #Yes or No
        'salt_content_in_the_diet': int,
        'alcohol_consumption_per_day': int,
        'Level_of_Stress': int,
        'Chronic_kidney_disease': int, # between 0 to 1,
        'Adrenal_and_thyroid_disorders': int}, # between 0 to 1,
    'Dataset2': {
        'Patient_Number': int, #eg. 1,2,3...100
        'Day_Number': int, #eg. 1,2,3...30
        'Physical_activity': int}
}