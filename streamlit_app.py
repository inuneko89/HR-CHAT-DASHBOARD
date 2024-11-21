import streamlit as st
import pandas as pd
import google.generativeai as genai
from datetime import datetime




def initialize_gemini():
    try:
        # Ensure API key configuration is correct
        genai.configure(api_key="AIzaSyAPJBFzTSfSLuLQfszrVsliBnoG-AFPf6k")
    except Exception as e:
        st.error(f"ไม่สามารถเชื่อมต่อกับ Gemini API: {str(e)}")

def load_hr_data():
    try:
        employee_data = pd.read_csv('employee_data_1511.csv')
        employee_skills = pd.read_csv('employee_skills_1511.csv')
        feedback_data = pd.read_csv('feedback_data_page.csv')
        kpi_data = pd.read_csv('kpi_data.csv')
        leave_data = pd.read_csv('leave_data_up.csv')
        task_data = pd.read_csv('task_data2_edit.csv')

        st.session_state.hr_data = {
            'employee_data': employee_data,
            'employee_skills': employee_skills,
            'feedback_data': feedback_data,
            'kpi_data': kpi_data,
            'leave_data': leave_data,
            'task_data': task_data
        }
        st.success("HR Data Loaded Successfully!")
        return st.session_state.hr_data
    except FileNotFoundError as e:
        st.error(f"ไม่พบไฟล์: {str(e)}")
    except pd.errors.EmptyDataError as e:
        st.error(f"ไฟล์ว่าง: {str(e)}")
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {str(e)}")
    return None







# Logout function to clear session
def logout():
    st.session_state.clear()  # Clear the session state
    st.success("คุณได้ออกจากระบบแล้ว")
    st.rerun()  # Reload the app to show the login page


def login_page():
    st.title("เข้าสู่ระบบ")
    
    # Create login form
    employee_id = st.text_input("Employee ID")  # New field
    username = st.text_input("ชื่อผู้ใช้")
    password = st.text_input("รหัสผ่าน", type="password")
    
    if st.button("เข้าสู่ระบบ"):
        # Simulate user authentication (replace this with real database or API check)
        user_database = {
            "101": {"username": "admin", "password": "password123", "role": "HR"},
            "102": {"username": "user1", "password": "user123", "role": "พนักงาน"}
        }
        
        if employee_id in user_database:
            user = user_database[employee_id]
            if username == user["username"] and password == user["password"]:
                st.session_state.logged_in = True
                st.session_state.employee_id = employee_id
                st.session_state.username = username
                st.session_state.role = user["role"]
                st.rerun()  # Reload the app without rendering additional UI elements
            else:
                st.error("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
        else:
            st.error("ไม่พบ Employee ID นี้ในระบบ")

def save_feedback_rating(feedback_scores):
    try:
        feedback_data = pd.read_csv('feedback_data_page.csv')  # Load existing feedback data
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Create new feedback entry
        new_feedback = pd.DataFrame([{
            'Employee_ID': st.session_state.employee_id,
            'Feedback_Type': "Sprint Feedback",
            'Colleague_Rating': feedback_scores['colleague'],
            'Process_Rating': feedback_scores['process'],
            'Task_Rating': feedback_scores['task'],
            'WorkLifeBalance_Rating': feedback_scores['work_life_balance'],
            'Environment_Rating': feedback_scores['work_environment'],
            'Timestamp': timestamp
        }])
        
        # Append new feedback to existing data
        feedback_data = pd.concat([feedback_data, new_feedback], ignore_index=True)
        feedback_data.to_csv('feedback_data_page.csv', index=False)
        st.success("Feedback ได้รับการบันทึกแล้ว")
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการบันทึก Feedback: {str(e)}")


def feedback_tab():
    st.header("กรุณาให้คะแนนและให้ Feedback สำหรับ sprint ที่ผ่านมา")
    
    # Sprint ID dropdown
    sprint_id = st.selectbox(
        "เลือก Sprint ID",
        options=["001", "002", "003", "004", "005"],
        key="sprint_id"
    )
    
    # Define feedback questions
    feedback_questions = {
        "colleague": "ใน sprint ที่ผ่านมา คุณมีความสุขกับเพื่อนร่วมงานแค่ไหน? (1 น้อย - 5 มาก)",
        "process": "ใน sprint ที่ผ่านมา คุณมีความสุขกับกระบวนการทำงานแค่ไหน? (1 น้อย - 5 มาก)",
        "task": "ใน sprint ที่ผ่านมา คุณมีความสุขกับงานที่ได้รับมอบหมายแค่ไหน? (1 น้อย - 5 มาก)",
        "work_life_balance": "ใน sprint ที่ผ่านมา คุณมีความสุขกับ work-life balance แค่ไหน? (1 น้อย - 5 มาก)",
        "work_environment": "ใน sprint ที่ผ่านมา คุณมีความสุขกับบรรยากาศในการทำงานแค่ไหน? (1 น้อย - 5 มาก)"
    }
    
    # Collect ratings
    feedback_scores = {}
    for key, question in feedback_questions.items():
        st.write(question)
        feedback_scores[key] = st.radio(
            label=f"เลือกคะแนนสำหรับ {key}",
            options=[1, 2, 3, 4, 5],
            horizontal=True,
            key=f"rating_{key}"
        )
    
    # Free text feedback
    feedback_comment = st.text_area("ความคิดเห็นเพิ่มเติม (ถ้ามี)")
    
    # Submit button
    if st.button("ส่ง Feedback"):
        save_feedback_rating(feedback_scores)  # Save rating-based feedback
        if feedback_comment:
            save_feedback(feedback_comment, sprint_id, feedback_type="comment")  # Save free-text feedback




def chatbot_response(prompt):
    try:
        # Use the correct method to call the Gemini model
        response = genai.generate(
            model="gemini-1.5-turbo",  # Replace with the correct model name if necessary
            prompt=prompt,
            temperature=0.7,
            max_tokens=150
        )
        return response['choices'][0]['text'].strip()  # Extract the text response
    except Exception as e:
        return f"เกิดข้อผิดพลาด: {str(e)}"

def save_feedback(feedback, sprint_id, feedback_type="general"):
    try:
        # Updated file name for better organization
        feedback_data = pd.read_csv('feedback_data_comment.csv')  
        
        # Add current timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # New feedback entry
        new_feedback = pd.DataFrame([{
            'Employee_ID': st.session_state.employee_id,  # Link feedback to the user
            'Sprint_ID': sprint_id,  # Add sprint ID
            'Feedback': feedback, 
            'Timestamp': timestamp,
            'Feedback_Type': feedback_type  # e.g., general, AI Interaction, Sprint-Specific
        }])
        
        # Append new feedback to existing data
        feedback_data = pd.concat([feedback_data, new_feedback], ignore_index=True)
        feedback_data.to_csv('feedback_data_comment.csv', index=False)  # Save updated data
        st.success("Feedback ได้รับการบันทึกแล้ว")
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการบันทึก Feedback: {str(e)}")


def main():
    st.set_page_config(page_title="HR Analytics Dashboard", page_icon="📊", layout="wide")
    
    # ตรวจสอบว่า 'hr_data' ถูกโหลดแล้วหรือยังใน session state
    if 'hr_data' not in st.session_state:
        load_hr_data()  # โหลดข้อมูล HR เมื่อยังไม่ได้โหลด
    
    # Initialize session state variables
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "employee_messages" not in st.session_state:
        st.session_state.employee_messages = []  # Initialize chat history for employees
    if "hr_messages" not in st.session_state:
        st.session_state.hr_messages = []  # Initialize chat history for HR users

    # Check login status
    if not st.session_state.logged_in:
        login_page()  # Show login page if not logged in
    else:
        st.title("📊 HR Analytics Dashboard")
        st.write("ระบบวิเคราะห์ข้อมูล HR ด้วย AI")
        
        # Initialize Gemini
        model = initialize_gemini()

        # Sidebar for user role selection
        with st.sidebar:
            st.header(f"Welcome, {st.session_state.username}")
            st.write(f"Employee ID: {st.session_state.employee_id}")
            st.write(f"บทบาทของคุณ: {st.session_state.role}")

            if st.session_state.role == "HR":
                st.header("ข้อมูล HR ที่มี")
                st.write("You have access to all the HR data.")
                for data_name, df in st.session_state.hr_data.items():
                    st.subheader(f"📁 {data_name}")
                    st.write("Columns:", ", ".join(df.columns.tolist()))
                
            if st.button("ออกจากระบบ"):
                logout()  # Logout button

        # HR or Employee-specific content
        if st.session_state.role == "พนักงาน":
            tab1, tab2 = st.tabs(["💬 ส่ง Feedback", "🤖 AI Assistant"])

            with tab1:
                feedback_tab()  # Use rating-based feedback tab

            with tab2:
                # Display chat history for Employees
                for message in st.session_state.employee_messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

                # Chat input
                if prompt := st.chat_input("ถามคำถามเกี่ยวกับข้อมูลบริษัทหรือข้อมูลทั่วไป..."):
                    st.session_state.employee_messages.append({"role": "user", "content": prompt})
                    with st.chat_message("user"):
                        st.markdown(prompt)

                    # Generate response using chatbot_response()
                    response = chatbot_response(prompt)
                    st.session_state.employee_messages.append({"role": "assistant", "content": response})
                    with st.chat_message("assistant"):
                        st.markdown(response)

        # If role is HR, display the HR AI Chatbot on the main page
        elif st.session_state.role == "HR":
            st.header("🤖 HR AI Chatbot")
            
            # Display chat history for HR users
            for message in st.session_state.hr_messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # Chat input
            if prompt := st.chat_input("ถามคำถามเกี่ยวกับข้อมูลบริษัทหรือข้อมูลทั่วไป..."):
                st.session_state.hr_messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                # Generate response using chatbot_response()
                response = chatbot_response(prompt)
                st.session_state.hr_messages.append({"role": "assistant", "content": response})
                with st.chat_message("assistant"):
                    st.markdown(response)

if __name__ == "__main__":
    main()
