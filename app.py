from flask import Flask, request, render_template, redirect, url_for, jsonify, session
from datetime import datetime
import mysql.connector
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a secure key

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Default XAMPP password (blank); update if you set a custom password
    'database': 'StudentRecordSystem'
}

# Helper function to validate email format
def validate_email(email):
    return bool(re.match(r'.+@.+\..+', email))

# Helper function to validate score range
def validate_score(score):
    try:
        score = float(score)
        return 0 <= score <= 100
    except ValueError:
        return False

# Helper function to validate date of birth
def validate_dob(dob):
    try:
        dob_date = datetime.strptime(dob, '%Y-%m-%d')
        return dob_date <= datetime.now()
    except ValueError:
        return False

# Login route
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Check if user exists
        cursor.execute("SELECT UserID, Password FROM User WHERE Username = %s", (username,))
        user = cursor.fetchone()

        if user and user[1] == password:
            session['user_id'] = user[0]
            # Check if the user is a student or admin
            cursor.execute("SELECT UserID FROM Student WHERE UserID = %s", (user[0],))
            if cursor.fetchone():
                session['role'] = 'student'
                return redirect(url_for('student_dashboard'))
            cursor.execute("SELECT UserID FROM Admin WHERE UserID = %s", (user[0],))
            if cursor.fetchone():
                session['role'] = 'admin'
                return redirect(url_for('admin_dashboard'))
        else:
            return render_template('login.html', error="Invalid username or password")

        cursor.close()
        conn.close()

    return render_template('login.html')

# Student dashboard
@app.route('/student/dashboard')
def student_dashboard():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))
    return render_template('student_dashboard.html', user_id=session['user_id'])

# Student view results
@app.route('/student/result', methods=['GET', 'POST'])
def student_result():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    if request.method == 'POST':
        subject_name = request.form.get('subject_name', '').strip()
        exam_level = request.form.get('exam_level', '').strip()
        session_name = request.form.get('session_name', '').strip()

        query = """
            SELECT u.FirstName, u.LastName, s.SubjectName, e.ExamLevel, ses.SessionName, r.Grade, r.Score,
                   GROUP_CONCAT(rd.Component) AS Components,
                   GROUP_CONCAT(rd.Weight) AS Weights,
                   GROUP_CONCAT(rd.ComponentScore) AS ComponentScores,
                   GROUP_CONCAT(rr.Remark) AS Remarks
            FROM Result r
            JOIN Student st ON r.StudentID = st.UserID
            JOIN User u ON st.UserID = u.UserID
            JOIN Examination e ON r.ExamID = e.ExamID
            JOIN Subject_Details s ON e.SubjectCode = s.SubjectCode AND e.ExamLevel = s.ExamLevel
            JOIN Session ses ON e.SessionID = ses.SessionID
            LEFT JOIN ResultDetail rd ON r.ResultID = rd.ResultID
            LEFT JOIN Result_Remarks rr ON r.ResultID = rr.ResultID
            WHERE st.UserID = %s
        """
        params = [user_id]

        conditions = []
        if subject_name:
            conditions.append("BINARY s.SubjectName = %s")
            params.append(subject_name)
        if exam_level:
            conditions.append("BINARY e.ExamLevel = %s")
            params.append(exam_level)
        if session_name:
            conditions.append("BINARY ses.SessionName = %s")
            params.append(session_name)

        if conditions:
            query += " AND " + " AND ".join(conditions)

        query += """
            GROUP BY r.ResultID, u.FirstName, u.LastName, s.SubjectName, e.ExamLevel, ses.SessionName, 
                     r.Grade, r.Score
        """

        cursor.execute(query, params)
        results = cursor.fetchall()

        cursor.close()
        conn.close()
        return render_template('student_result.html', results=results, user_id=user_id)

    cursor.close()
    conn.close()
    return render_template('student_result.html', results=None, user_id=user_id)

# Admin dashboard
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    return render_template('admin_dashboard.html', user_id=session['user_id'])

@app.route('/admin/fetch_result', methods=['POST'])
def admin_fetch_result():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    student_id = request.form.get('student_id')
    subject_name = request.form.get('subject_name', '').strip()
    exam_level = request.form.get('exam_level', '').strip()
    session_name = request.form.get('session_name', '').strip()

    if not student_id:
        return jsonify({'error': 'Student ID is required'}), 400

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    query = """
        SELECT r.ResultID, u.FirstName, u.LastName, s.SubjectName, e.ExamLevel, ses.SessionName, 
               r.Grade, r.Score, r.ResultDate, r.Status,
               GROUP_CONCAT(rd.Component) AS Components,
               GROUP_CONCAT(rd.Weight) AS Weights,
               GROUP_CONCAT(rd.ComponentScore) AS ComponentScores,
               GROUP_CONCAT(rr.Remark) AS Remarks
        FROM Result r
        JOIN Student st ON r.StudentID = st.UserID
        JOIN User u ON st.UserID = u.UserID
        JOIN Examination e ON r.ExamID = e.ExamID
        JOIN Subject_Details s ON e.SubjectCode = s.SubjectCode AND e.ExamLevel = s.ExamLevel
        JOIN Session ses ON e.SessionID = ses.SessionID
        LEFT JOIN ResultDetail rd ON r.ResultID = rd.ResultID
        LEFT JOIN Result_Remarks rr ON r.ResultID = rr.ResultID
        WHERE st.UserID = %s
    """
    params = [student_id]

    conditions = []
    if subject_name:
        conditions.append("BINARY s.SubjectName = %s")
        params.append(subject_name)
    if exam_level:
        conditions.append("BINARY e.ExamLevel = %s")
        params.append(exam_level)
    if session_name:
        conditions.append("BINARY ses.SessionName = %s")
        params.append(session_name)

    if conditions:
        query += " AND " + " AND ".join(conditions)

    query += """
        GROUP BY r.ResultID, u.FirstName, u.LastName, s.SubjectName, e.ExamLevel, ses.SessionName, 
                 r.Grade, r.Score, r.ResultDate, r.Status
    """

    cursor.execute(query, params)
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    if not results:
        return jsonify({'message': 'No results found'})
    return jsonify({'results': results})

# Admin add result
@app.route('/admin/add_result', methods=['POST'])
def admin_add_result():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    result_id = request.form['result_id']
    student_id = request.form['student_id']
    exam_id = request.form['exam_id']
    grade = request.form['grade']
    score = request.form['score']
    result_date = request.form['result_date']
    status = request.form['status']
    components = request.form.getlist('components[]')
    component_scores = request.form.getlist('component_scores[]')
    weights = request.form.getlist('weights[]')
    remarks = request.form.getlist('remarks[]')

    # Validate inputs
    if grade not in ['A*', 'A', 'B', 'C', 'D', 'E', 'F', 'U']:
        return jsonify({'error': 'Invalid grade'}), 400
    if not validate_score(score):
        return jsonify({'error': 'Score must be between 0 and 100'}), 400
    if status not in ['Published', 'Pending']:
        return jsonify({'error': 'Invalid status'}), 400
    try:
        datetime.strptime(result_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid result date format'}), 400

    for cs, w in zip(component_scores, weights):
        if not validate_score(cs):
            return jsonify({'error': 'Component score must be between 0 and 100'}), 400
        try:
            w = float(w)
            if not (0 <= w <= 1):
                return jsonify({'error': 'Weight must be between 0 and 1'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid weight format'}), 400

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        # Insert into Result
        cursor.execute("""
            INSERT INTO Result (ResultID, StudentID, ExamID, Grade, Score, ResultDate, Status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (result_id, student_id, exam_id, grade, score, result_date, status))

        # Insert into ResultDetail
        for i, (comp, cs, w) in enumerate(zip(components, component_scores, weights)):
            cursor.execute("""
                INSERT INTO ResultDetail (ResultID, DetailID, Component, ComponentScore, Weight)
                VALUES (%s, %s, %s, %s, %s)
            """, (result_id, f'D{i+1}', comp, cs, w))

        # Insert into Result_Remarks
        for remark in remarks:
            if remark:  # Only insert non-empty remarks
                cursor.execute("""
                    INSERT INTO Result_Remarks (ResultID, Remark)
                    VALUES (%s, %s)
                """, (result_id, remark))

        # Log admin action
        cursor.execute("""
            INSERT INTO AdminResultManagement (AdminID, ResultID, Action, ActionDate)
            VALUES (%s, %s, %s, %s)
        """, (session['user_id'], result_id, 'Add', datetime.now()))

        conn.commit()
        return jsonify({'success': 'Result added successfully'})
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()

# Admin update result
@app.route('/admin/update_result', methods=['POST'])
def admin_update_result():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    result_id = request.form['result_id']
    grade = request.form['grade']
    score = request.form['score']
    status = request.form['status']
    components = request.form.getlist('components[]')
    component_scores = request.form.getlist('component_scores[]')
    weights = request.form.getlist('weights[]')
    remarks = request.form.getlist('remarks[]')

    # Validate inputs
    if grade not in ['A*', 'A', 'B', 'C', 'D', 'E', 'F', 'U']:
        return jsonify({'error': 'Invalid grade'}), 400
    if not validate_score(score):
        return jsonify({'error': 'Score must be between 0 and 100'}), 400
    if status not in ['Published', 'Pending']:
        return jsonify({'error': 'Invalid status'}), 400

    for cs, w in zip(component_scores, weights):
        if not validate_score(cs):
            return jsonify({'error': 'Component score must be between 0 and 100'}), 400
        try:
            w = float(w)
            if not (0 <= w <= 1):
                return jsonify({'error': 'Weight must be between 0 and 1'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid weight format'}), 400

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        # Update Result
        cursor.execute("""
            UPDATE Result
            SET Grade = %s, Score = %s, Status = %s
            WHERE ResultID = %s
        """, (grade, score, status, result_id))

        # Delete existing ResultDetail and Result_Remarks
        cursor.execute("DELETE FROM ResultDetail WHERE ResultID = %s", (result_id,))
        cursor.execute("DELETE FROM Result_Remarks WHERE ResultID = %s", (result_id,))

        # Insert new ResultDetail
        for i, (comp, cs, w) in enumerate(zip(components, component_scores, weights)):
            cursor.execute("""
                INSERT INTO ResultDetail (ResultID, DetailID, Component, ComponentScore, Weight)
                VALUES (%s, %s, %s, %s, %s)
            """, (result_id, f'D{i+1}', comp, cs, w))

        # Insert new Result_Remarks
        for remark in remarks:
            if remark:
                cursor.execute("""
                    INSERT INTO Result_Remarks (ResultID, Remark)
                    VALUES (%s, %s)
                """, (result_id, remark))

        # Log admin action
        cursor.execute("""
            INSERT INTO AdminResultManagement (AdminID, ResultID, Action, ActionDate)
            VALUES (%s, %s, %s, %s)
        """, (session['user_id'], result_id, 'Update', datetime.now()))

        conn.commit()
        return jsonify({'success': 'Result updated successfully'})
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/delete_result', methods=['POST'])
def admin_delete_result():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    result_id = request.form.get('result_id')

    if not result_id:
        return jsonify({'error': 'Result ID is required'}), 400

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        # Check if the ResultID exists
        cursor.execute("SELECT COUNT(*) FROM Result WHERE ResultID = %s", (result_id,))
        if cursor.fetchone()[0] == 0:
            return jsonify({'error': 'Result ID not found'}), 404

        # Delete related records in dependent tables first
        cursor.execute("DELETE FROM Result_Remarks WHERE ResultID = %s", (result_id,))
        cursor.execute("DELETE FROM ResultDetail WHERE ResultID = %s", (result_id,))
        cursor.execute("DELETE FROM AdminResultManagement WHERE ResultID = %s", (result_id,))
        cursor.execute("DELETE FROM Result WHERE ResultID = %s", (result_id,))

        conn.commit()
        return jsonify({'success': 'Result deleted successfully'})
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/view_all_results')
def admin_view_all_results():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Fetch all results for IGCSE and A-Level, aggregating components and remarks
    query = """
        SELECT u.FirstName, u.LastName, s.SubjectName, e.ExamLevel, ses.SessionName, 
               r.Grade, r.Score, r.ResultDate, r.Status,
               GROUP_CONCAT(rd.Component) AS Components,
               GROUP_CONCAT(rd.Weight) AS Weights,
               GROUP_CONCAT(rd.ComponentScore) AS ComponentScores,
               GROUP_CONCAT(rr.Remark) AS Remarks
        FROM Result r
        JOIN Student st ON r.StudentID = st.UserID
        JOIN User u ON st.UserID = u.UserID
        JOIN Examination e ON r.ExamID = e.ExamID
        JOIN Subject_Details s ON e.SubjectCode = s.SubjectCode AND e.ExamLevel = s.ExamLevel
        JOIN Session ses ON e.SessionID = ses.SessionID
        LEFT JOIN ResultDetail rd ON r.ResultID = rd.ResultID
        LEFT JOIN Result_Remarks rr ON r.ResultID = rr.ResultID
        GROUP BY r.ResultID, u.FirstName, u.LastName, s.SubjectName, e.ExamLevel, ses.SessionName, 
                 r.Grade, r.Score, r.ResultDate, r.Status
        ORDER BY e.ExamLevel, s.SubjectName
    """
    cursor.execute(query)
    results = cursor.fetchall()

    # Organize results by exam level and subject
    igcse_results = {}
    alevel_results = {}
    for result in results:
        exam_level = result[3]
        subject = result[2]
        if exam_level == 'IGCSE':
            if subject not in igcse_results:
                igcse_results[subject] = []
            igcse_results[subject].append(result)
        elif exam_level == 'A-Level':
            if subject not in alevel_results:
                alevel_results[subject] = []
            alevel_results[subject].append(result)

    cursor.close()
    conn.close()
    return render_template('admin_dashboard.html', igcse_results=igcse_results, alevel_results=alevel_results, user_id=session['user_id'])

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(debug=True, port=5001)  # Change to port 5001