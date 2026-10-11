def check_teacher_clash(timetable, teacher, day, period):
    """Checks if the teacher is already assigned to another class in the same slot."""
    for entry in timetable:
        if entry['day'] == day and entry['period'] == period and entry['teacher'] == teacher:
            return True
    return False

def check_room_clash(timetable, room, day, period):
    """Checks if the room is already occupied in the same slot."""
    for entry in timetable:
        if entry['day'] == day and entry['period'] == period and entry['room'] == room:
            return True
    return False

def check_max_classes_per_day(timetable, subject, day, max_classes):
    """Checks if a subject has reached its daily limit."""
    count = 0
    for entry in timetable:
        if entry['day'] == day and entry['subject'] == subject:
            count += 1
    return count >= max_classes

def is_valid_assignment(timetable, assignment, constraints):
    """Validates if a specific assignment satisfies all constraints."""
    day = assignment['day']
    period = assignment['period']
    teacher = assignment['teacher']
    room = assignment['room']
    subject = assignment['subject']
    
    # Check fixed breaks
    if period in constraints.get('break_periods', []):
        return False
        
    if check_teacher_clash(timetable, teacher, day, period):
        return False
        
    if check_room_clash(timetable, room, day, period):
        return False
        
    if check_max_classes_per_day(timetable, subject, day, constraints.get('max_classes_per_day', 2)):
        return False
        
    return True
