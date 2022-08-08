from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:default@localhost:5432/university_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Group(db.Model):
    __tablename__ = "groups"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(5))

    students = db.relationship("Student", backref='groups')

    def __repr__(self):
        return f"Group(id={self.id}, name={self.name})"


association_table = db.Table(
    "association",
    db.Column("student_id", db.ForeignKey("students.id"), primary_key=True),
    db.Column("course_id", db.ForeignKey("courses.id"), primary_key=True),
)


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)

    courses = db.relationship(
        "Course", secondary=association_table, backref="students"
    )

    def __repr__(self):
        return f"Student(id={self.id}, group_id={self.group_id}, first_name={self.first_name}, last_name={self.last_name})"


class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return f"Course(id={self.id}, name={self.name}, description={self.description})"

courses_dict = {"discrete_math": "Discrete Math",
                "physics" : "Physics",
                "math_analysis": "Math Analysis",
                "english" : "English",
                "programming": "Programming",
                "symmetric_cryptography": "Symmetric Cryptography",
                "asymmetric_cryptography": "Asymmetric Cryptography",
                "combinatorial_analysis": "Combinatorial Analysis",
                "algorithms": "Algorithms",
                "statistics" : "Statistics"}

@app.route('/')
def base():
    return render_template("base.html")


@app.route('/students/')
def all_students():
    the_students = Student.query.all()
    return render_template("students_table.html", the_students=the_students, title="Students")


@app.route('/groups/', methods=['GET'])
def all_groups():
    count = request.args.get('count')
    if count is None:
        the_groups = Group.query.all()
        return render_template("groups_table.html", the_groups=the_groups, title="Groups")
    else:
        groups_counted = db.session.query(Group.id, Group.name, func.count(Student.group_id).label('n_students')) \
            .join(Student).group_by(Group.id).having(func.count(Student.group_id) <= count).all()
        return render_template("groups_by_count.html", groups_counted=groups_counted, the_count=count,
                               title="Groups by count")


@app.route('/courses/')
def all_courses():
    the_courses = Course.query.all()
    return render_template("courses_table.html", the_courses=the_courses, title="Courses")

@app.route('/courses/as_list')
def list_courses():
    return render_template("courses_list.html", courses_dict=courses_dict)

@app.route('/courses/<coursename>/students')
def students_on_course(coursename):
    course_full_name = courses_dict[coursename]
    students_lst = db.session.query(Student.first_name, Student.last_name).join(association_table).join(Course) \
        .filter(Course.name == course_full_name).all()
    return render_template("students_on_course.html", students_lst=students_lst, coursename=course_full_name)




if __name__ == '__main__':
    app.run(debug=True)