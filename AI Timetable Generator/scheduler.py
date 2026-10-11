import random
from constraints import is_valid_assignment

class TTRScheduler:
    def __init__(self, data):
        self.days = data['days']
        self.periods = list(range(1, data['periods_per_day'] + 1))
        self.subjects = data['subjects']
        self.teachers = data['teachers']
        self.rooms = data['rooms']
        self.constraints = {
            'max_classes_per_day': data.get('max_classes_per_day', 2),
            'break_periods': data.get('break_periods', [])
        }
        self.timetable = []

    def generate(self):
        """Simple backtracking-like approach to generate a valid timetable."""
        self.timetable = []
        
        # Shuffle subjects to get different results each time
        shuffled_subjects = list(self.subjects)
        random.shuffle(shuffled_subjects)
        
        # Target total periods to fill (e.g., each subject should have N periods per week)
        # For simplicity, let's try to assign each subject 5 times a week
        target_load = 5 
        
        for subject in shuffled_subjects:
            teacher = self.teachers[subject]
            assigned_count = 0
            
            # Try to assign 'target_load' slots for each subject
            for _ in range(target_load):
                # Shuffle slots to avoid patterns
                all_slots = [(d, p) for d in self.days for p in self.periods]
                random.shuffle(all_slots)
                
                success = False
                for day, period in all_slots:
                    # Try each room
                    shuffled_rooms = list(self.rooms)
                    random.shuffle(shuffled_rooms)
                    
                    for room in shuffled_rooms:
                        assignment = {
                            'day': day,
                            'period': period,
                            'subject': subject,
                            'teacher': teacher,
                            'room': room
                        }
                        
                        if is_valid_assignment(self.timetable, assignment, self.constraints):
                            self.timetable.append(assignment)
                            success = True
                            assigned_count += 1
                            break
                    if success:
                        break
        
        return self.timetable
