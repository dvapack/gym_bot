import pandas as pd

class Dataloader:
    def __init__(self, csv_file):
        self.data_csv = pd.read_csv(csv_file)

    def set_order(self):
        self.data_csv['Date'] = pd.to_datetime(self.data_csv['Date'])
        self.data_csv = self.data_csv.sort_values(['Date', 'Exercise'])
        self.data_csv['Set Number'] = self.data_csv.groupby(['Date', 'Exercise']).cumcount() + 1
        columns = ['Date', 'Exercise', 'Category', 'Set Number', 'Weight', 'Reps']
        self.data_csv = self.data_csv[columns]
    
    def filter_data(self):
        self.data_csv = self.data_csv.dropna(subset=['Date', 'Exercise', 'Category', 'Weight', 'Reps'])


    def get_muscle_groups(self):
        return self.data_csv['Category'].unique().tolist()
    
    def get_exercises_by_muscle_group(self, muscle_group):
        filtered = self.data_csv[self.data_csv['Category'] == muscle_group]
        return filtered['Exercise'].unique().tolist()
    
    def get_workouts(self):
        workouts = {}
        for _, row in self.data_csv.iterrows():
            workout_date = row['Date']
            if workout_date not in workouts:
                workouts[workout_date] = {
                    'date': row['Date'],
                    'sets': []
                }
            workouts[workout_date]['sets'].append({
                'exercise': row['Exercise'],
                'muscle_group': row['Category'],
                'reps': row['Reps'],
                'weight': row['Weight'],
                'set_number': row['Set Number']
            })
        return workouts