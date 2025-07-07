"""
AI Service for intelligent timetable generation using Gemini or Groq
"""

import os
import json
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# AI Provider Configuration
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini").lower()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class AITimetableService:
    """AI-powered timetable generation service"""
    
    def __init__(self):
        self.provider = AI_PROVIDER
        self.setup_ai_client()
    
    def setup_ai_client(self):
        """Setup AI client based on provider"""
        if self.provider == "gemini" and GEMINI_API_KEY:
            try:
                import google.generativeai as genai
                genai.configure(api_key=GEMINI_API_KEY)
                self.client = genai.GenerativeModel('gemini-pro')
                self.available = True
            except ImportError:
                print("⚠️ Gemini AI not available. Install google-generativeai package.")
                self.available = False
        elif self.provider == "groq" and GROQ_API_KEY:
            try:
                from groq import Groq
                self.client = Groq(api_key=GROQ_API_KEY)
                self.available = True
            except ImportError:
                print("⚠️ Groq AI not available. Install groq package.")
                self.available = False
        else:
            print("⚠️ No AI provider configured. Using fallback algorithm.")
            self.available = False
    
    def generate_timetable_suggestions(self, 
                                     subjects: List[Dict], 
                                     staff: List[Dict], 
                                     classrooms: List[Dict], 
                                     time_slots: List[Dict],
                                     constraints: Dict) -> Dict[str, Any]:
        """Generate AI-powered timetable suggestions"""
        
        if not self.available:
            return self.fallback_timetable_generation(subjects, staff, classrooms, time_slots, constraints)
        
        try:
            # Prepare data for AI
            context = self.prepare_ai_context(subjects, staff, classrooms, time_slots, constraints)
            
            if self.provider == "gemini":
                return self.generate_with_gemini(context)
            elif self.provider == "groq":
                return self.generate_with_groq(context)
            else:
                return self.fallback_timetable_generation(subjects, staff, classrooms, time_slots, constraints)
                
        except Exception as e:
            print(f"❌ AI generation failed: {e}")
            return self.fallback_timetable_generation(subjects, staff, classrooms, time_slots, constraints)
    
    def prepare_ai_context(self, subjects, staff, classrooms, time_slots, constraints):
        """Prepare context for AI model"""
        return {
            "subjects": subjects,
            "staff": staff,
            "classrooms": classrooms,
            "time_slots": time_slots,
            "constraints": constraints,
            "task": "Generate an optimal timetable allocation"
        }
    
    def generate_with_gemini(self, context):
        """Generate timetable using Gemini AI"""
        prompt = f"""
        You are an expert timetable scheduling AI for SRM College. Generate an optimal timetable based on the following data:

        SUBJECTS: {json.dumps(context['subjects'], indent=2)}
        STAFF: {json.dumps(context['staff'], indent=2)}
        CLASSROOMS: {json.dumps(context['classrooms'], indent=2)}
        TIME_SLOTS: {json.dumps(context['time_slots'], indent=2)}
        CONSTRAINTS: {json.dumps(context['constraints'], indent=2)}

        RULES:
        1. No staff member can have overlapping classes
        2. No classroom can be double-booked
        3. Respect lunch break timings
        4. Balance workload across days
        5. Prefer theory classes in morning, labs in afternoon
        6. Minimize gaps in staff schedules

        Return a JSON response with:
        {{
            "timetable": [
                {{
                    "day": "Monday",
                    "time_slot_id": 1,
                    "subject_id": 1,
                    "staff_id": 1,
                    "classroom_id": 1,
                    "confidence": 0.95
                }}
            ],
            "conflicts": [],
            "suggestions": [],
            "optimization_score": 0.85
        }}
        """
        
        try:
            response = self.client.generate_content(prompt)
            # Parse JSON from response
            result = json.loads(response.text)
            return result
        except Exception as e:
            print(f"Gemini generation error: {e}")
            return self.fallback_timetable_generation(
                context['subjects'], context['staff'], 
                context['classrooms'], context['time_slots'], 
                context['constraints']
            )
    
    def generate_with_groq(self, context):
        """Generate timetable using Groq AI"""
        prompt = f"""
        Generate an optimal timetable for SRM College based on this data:
        
        Subjects: {context['subjects']}
        Staff: {context['staff']}
        Classrooms: {context['classrooms']}
        Time Slots: {context['time_slots']}
        Constraints: {context['constraints']}
        
        Return optimized timetable as JSON with conflict resolution.
        """
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an expert timetable scheduling AI."},
                    {"role": "user", "content": prompt}
                ],
                model="mixtral-8x7b-32768",
                temperature=0.3,
                max_tokens=2000
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            print(f"Groq generation error: {e}")
            return self.fallback_timetable_generation(
                context['subjects'], context['staff'], 
                context['classrooms'], context['time_slots'], 
                context['constraints']
            )
    
    def fallback_timetable_generation(self, subjects, staff, classrooms, time_slots, constraints):
        """Fallback algorithm when AI is not available"""
        print("🔄 Using fallback timetable generation algorithm...")
        
        timetable = []
        conflicts = []
        staff_schedule = {}
        classroom_schedule = {}
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        
        # Initialize schedules
        for day in days:
            staff_schedule[day] = {}
            classroom_schedule[day] = {}
            for slot in time_slots:
                staff_schedule[day][slot['id']] = None
                classroom_schedule[day][slot['id']] = []
        
        # Assign subjects to time slots
        for subject in subjects:
            if not subject.get('assigned_staff_id'):
                continue
                
            total_hours = subject.get('theory_hours', 3) + subject.get('practical_hours', 0)
            hours_assigned = 0
            
            for day in days:
                if hours_assigned >= total_hours:
                    break
                    
                for slot in time_slots:
                    if hours_assigned >= total_hours:
                        break
                    
                    slot_id = slot['id']
                    staff_id = subject['assigned_staff_id']
                    
                    # Check staff availability
                    if staff_schedule[day][slot_id] is not None:
                        continue
                    
                    # Find available classroom
                    suitable_classrooms = [
                        c for c in classrooms 
                        if c['id'] not in classroom_schedule[day][slot_id] and
                        c.get('is_available', True) and
                        (c.get('room_type') == 'Lab' if subject.get('practical_hours', 0) > 0 else True)
                    ]
                    
                    if not suitable_classrooms:
                        continue
                    
                    # Assign to timetable
                    classroom = suitable_classrooms[0]
                    
                    timetable.append({
                        "day": day,
                        "time_slot_id": slot_id,
                        "subject_id": subject['id'],
                        "staff_id": staff_id,
                        "classroom_id": classroom['id'],
                        "confidence": 0.8
                    })
                    
                    # Update schedules
                    staff_schedule[day][slot_id] = staff_id
                    classroom_schedule[day][slot_id].append(classroom['id'])
                    hours_assigned += 1
        
        return {
            "timetable": timetable,
            "conflicts": conflicts,
            "suggestions": [
                "Consider balancing workload across days",
                "Schedule labs in afternoon slots when possible",
                "Minimize gaps in staff schedules"
            ],
            "optimization_score": 0.75
        }
    
    def detect_conflicts(self, timetable_entries):
        """Detect conflicts in timetable"""
        conflicts = []
        staff_slots = {}
        classroom_slots = {}
        
        for entry in timetable_entries:
            key = f"{entry['day']}_{entry['time_slot_id']}"
            
            # Check staff conflicts
            if entry['staff_id'] in staff_slots.get(key, []):
                conflicts.append(f"Staff conflict: Staff {entry['staff_id']} has multiple classes at {entry['day']} slot {entry['time_slot_id']}")
            else:
                if key not in staff_slots:
                    staff_slots[key] = []
                staff_slots[key].append(entry['staff_id'])
            
            # Check classroom conflicts
            if entry['classroom_id'] in classroom_slots.get(key, []):
                conflicts.append(f"Classroom conflict: Room {entry['classroom_id']} is double-booked at {entry['day']} slot {entry['time_slot_id']}")
            else:
                if key not in classroom_slots:
                    classroom_slots[key] = []
                classroom_slots[key].append(entry['classroom_id'])
        
        return conflicts
    
    def optimize_timetable(self, timetable_entries):
        """Optimize existing timetable"""
        # Implement optimization logic
        suggestions = []
        
        # Check for gaps in staff schedules
        staff_daily_slots = {}
        for entry in timetable_entries:
            staff_id = entry['staff_id']
            day = entry['day']
            
            if staff_id not in staff_daily_slots:
                staff_daily_slots[staff_id] = {}
            if day not in staff_daily_slots[staff_id]:
                staff_daily_slots[staff_id][day] = []
            
            staff_daily_slots[staff_id][day].append(entry['time_slot_id'])
        
        # Suggest improvements
        for staff_id, daily_slots in staff_daily_slots.items():
            for day, slots in daily_slots.items():
                if len(slots) > 1:
                    slots.sort()
                    gaps = []
                    for i in range(len(slots) - 1):
                        if slots[i+1] - slots[i] > 1:
                            gaps.append(f"Gap between slots {slots[i]} and {slots[i+1]}")
                    
                    if gaps:
                        suggestions.append(f"Staff {staff_id} has gaps on {day}: {', '.join(gaps)}")
        
        return suggestions

# Global AI service instance
ai_service = AITimetableService()