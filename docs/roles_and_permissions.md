# Authorization

These are the user roles.

| Role          | Description                                            |
|---------------|--------------------------------------------------------|
| Anonymous     | Anonymous is an implicit role; it is not implemented.  |
| Teacher       | Teachers buy courses.                                  |
| Instructor    | Instructors own the course that the CCX is based on.   |
| Administrator | Administrator is a default role provided by Django.    |


This table represents authorizations as a triple; 
who can do it, what can they do, and where can they do it. The
"Who" are the columns, the "Where" are the rows, and the "What"
is in the cells.

| Permissions Table    | Anonymous | Teacher   | Instructor | Admin |
|----------------------|-----------|-----------|------------|-------|
| course/module list   | view      | view, buy | view, edit | all   |
| course/module detail | view (1)  | view, buy | view, edit | all   |
| course price         |           | view      | view, edit | all   |
| course description   |           | view      | view, edit | all   |
| course liveness      |           |           | edit       | all   |

(1) Anonymous users have a limited view of course/module detail. They
can see only title, image, and blurb. No buy or cart tab.
