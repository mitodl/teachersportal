Release Notes
=============

Version 0.3.0
-------------

- Release 0.2.0
- Navigating between courses no longer keeps stale state.
- Used urljoin to create url for ccxcon API
- Removed check that required a cart to contain all modules for a course
- Implemented consistent dollar formatting
- Add links to footer.
- Fixed snackbar
- Fixed CSS layout for activation page
- Changed seat count to textbox, changed slider&#39;s step to 1
- Implemented popup of login after successful activation
- Added tests to increase coverage
- Adding github PR template.
- Implemented PATCH for course API
- Fixed header overlap
- Made courses which are not live visible to instructors, and added a live flag
- Added delete button, other cart UI updates
- Fixed React CSS for Homepage card
- Added back React hot reloading with fixed version of webpack
- Added uuid to module admin

Release Notes
=============

Version 0.2.0
-------------

- Implemented checks to enforce permissions for checkout API
- Changed CCX post to be per course instead of per module
- Redirect on logout.
- Anonymous users can see limited part of the course details
- Small changes on test requirements and docker-compose
- Added test for login while logged in
- Added permissions API
- Remove text from homepage.
- Remove content tab.
- Makes the header look like the mockup.
- Refactored tests and CourseDetail component
- Fixed snackbar dispatch
- Pull out course-list into its own component
- Improved UX for activation page
- Addressed review comments
- Move to django-server-status.
- Added permissions and instructor group
- Added migration to match model change for instance
- Added shrinkwrap file to pin versions
- Altered cart to move seats count to the course level
- Removed external links
- Capture conversions.
- Added proposal for dealing with updating courses.
- Added cart item validation
- Adjusted progress bar shown while loading course content.
- Fixed cart total calculation
- Build fix.
- Management command to generate prices for modules
- Improve the look &amp; feel of the admin.
- Push dispatch method into login modal.
- Implemented Course Card and Course Listing.
- Added str implementations to models
- Removed authentication for course list view
- Added instance field and implemented code to store data from webhooks
- Pylint
- Address comments
- Added success and failure messages for checkout
- Refactored product API
- Fixed snackbar to only display once per message
- Implemented Snackbar
- Changed 400 to 500 error to reflect internal problem
- Added course_modules to CCX POST, and switched to using JSON
- Removed django-oscar
- Split webpack config into dev and production files
- Added total field to checkout API
- Installed pip via get-pip.py to fix requests installation
- Added ProductException
- Fixed login modal layout
- Completed basic integration of Google Analytics, wuth both page and tab views logged.
- Added tests to verify that seats must be integers
- Remove Continuous Testing instructions
- Updated OS X development configuration instructions
- Added integration tests, refactored test utility code
- Support for zendesk.
- Move all reducers to handleActions
- Use actual data for images and descriptions.
- Turned on minimization, sourcemaps
- use react-actions to clean up action generators.
- Users must purchase full courses
- Calculate total on both slider move and chapter select.
- Added test for checkout authorization
- Post to CCXCon on successful purchase.
- Revert comments in docker-compose.yml.
- Add loading progress indicator to course detail page.
- Faster builds by *only* double installing deps.
- Filtered out products from cart which aren&#39;t accessible in the API anymore
- Implemented submit on enter keypress for login and registration
- Fixed cookie handling on chrome
- Implemented product list in redux
- Fix minor issues from Shopping Cart PR (#147).
- Implemented status API
- Add shopping cart UI.
- Added missing settings from app.json with sane requirements
- Add logging around product not available.
- Removed categories from modules, which are invalid
- Tied cart to localStorage
- Add debug logging to the hmac verification code

Version 0.1.0
-------------

- Initial version

