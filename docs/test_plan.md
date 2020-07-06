# Teacher's Portal Test Plan

## Authentication/Authorization

Teacher's Portal is visible to the Internet. Roles and permissions are
described in another file: ``docs/roles_and_permissions.md``


## Courses

### Show available courses

The test starts with the user not signed in.

Action | Result | Notes
--- | --- | ---
Navigate to TP | you see MIT Courseware Marketplace | The blue button should say "SIGN IN OR REGISTER"
 | You should see the courses available for purchase |
Log in as a teacher | The course list shouldn't change |

Relevant Issues:

- [Course view for anonymous users #303](https://github.com/mitodl/teachersportal/issues/303)
- Course doesn't render in Firefox bug - #137
- [teacher view of course - #3](https://github.com/mitodl/teachersportal/issues/3)


### Show course detail

The user's view of a course depends on their role.

Action | Result | Notes
--- | --- | ---
Click on a course to select it | You should see the course detail with two tabs, 'About' and 'Buy'  |

### As an instructor, show the courses I’ve authored

Action | Result | Notes
--- | --- | ---
 Log in as an instructor | confirm that the courses listed include all the courses you authored |

Relevant Issues:

- [As an instructor, I’d like see the courses I’ve authored. -  #51](https://github.com/mitodl/teachersportal/issues/51)

### As a teacher, buy course seats

Action | Result | Notes
--- | --- | ---
Log in as a teacher |  |

 Relevant Issues:

- [Content Tab Component for Teachers (react) - #48](https://github.com/mitodl/teachersportal/issues/48)
- [Tabs Component (static) - #47](https://github.com/mitodl/teachersportal/issues/47)


### Add a title to the page - #20

### teacher registration duplicate - #25

### View basic course info - #28

### List course modules instructor dashboard - #29

### Shell Components (static) - #44

### Intro Page components - #45

### Course Info Component for Teachers (static) - #46


### "about" tab comes from teachers - #83

### Authenticate to CCXCon - #85

### On GET /ccxcon/... there is an exception regarding hop-by-hop errors - #106

### Registration - #121

### Complete buy tab in course detail view - #126

### Login - #130

### Sanitize course description HTML - #140

### Add redirect parameter to registration email - #142

### Better UI for activation Needs Review - #152

### Better UI for registration success message - #153

### Review E-mail config - #159

### Course detail page UI: loading indicator needed - #161

Action | Result | Notes
--- | --- | ---
 |  |

### Course detail page UI: on the buy tab, move the "chapters" table heading left - #162

### Course detail page UI: seat quantity slider feedback - #163

### Use 'MIT Teacher's Portal' in user facing content - #164

### Index page - #167

### Sync cart to local storage - #168

### TP should post to CCXCon on successful purchase. - #173

### Oscar product dashboard: "Product with this UPC already exists" - #174

### Remove unused UI pieces - #177

### Handle an invalid cart - #180

### Don't escape HTML for course detail - #182

### pressing enter in the sign-in form should submit the form. - #183

### Data integrity problem when posting Modules via webhook bug - #185

### Change maxSeats const from 1000 to 200 - #192

### Unable to sign out using Sign Out button in Chrome - #197

### portal/util shouldn't use bare exceptions - #201

### Pull Real Course Images from edX - #205

### Use short description from edX course - #206

### Calculate cart total on the buy tab and in the cart before checkout - #207

### Add cart total to checkout API request, verify that that number matches the one we calculate in Python - #209

### Create CCXs using Celery instead of through the web process - #212

### Clicking "all" checkbox should uncheck items bug - #216

### Verify that all modules of a chapter are added to the cart, or else error - #218

### If user doesn't register with correct email, fulfillment fails. - #219

### Authorization test for checkout API - #222

### Message for user on checkout failure/success - #226

### Fix login/registration dialog to show fields side by side - #234

### Server should return a 500 on CCX create failure, not a 400 - #254

### Keep track of snackbar history so we don't show the same message repeatedly - #265

### Allow GET /courses without authentication - #270

### When user clicks a course detail link, pop up login dialog if necessary in progress - #275

### Allow user to see ZenDesk conversation in Teacher's Portal - #276

### Different total values in cart and in stripe checkout modal - #284

### Fix seat count cart granularity - #286

### Links on course listing page should show link cursor when hovering over them - #289

### Make upper left MIT icon a link back to course listing - #292

### Show course title as well as module title in cart panel - #293



## Issues that are still open

### instructor registration instructor dashboard - #26

Unimplemented. Defer testing until issue is closed.

### list edX courses for commercial CCX use instructor dashboard - #27

Unimplemented. Defer testing until issue is closed.

### Publish switch for courses instructor dashboard - #30

This one is still open, until the UI is ready you can (and may need to)
do it through the Django admin dashboard.

### Set price for module instructor dashboard - #32

This one is still open, until the UI is ready you can (and may need to)
do it through the Django admin dashboard.

### Clear course data when user goes to course listing page - #279
### Log out from anywhere should redirect to / - #281
### Format dollars consistently - #288
### Show subchapters when hovering over each module in the course content - #291
### Make real links for footer content - #294
### Allow people to remove items from their shopping carts. - #296
