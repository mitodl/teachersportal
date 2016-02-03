# Teacher's Portal: Updating courses

Teacher's Portal (TP) currently supports creating Custom 
Courses (CCX) in edX via ccxcon. We don't yet support 
updating. This document aims to articulate the edge cases therein.

## User flow

A user, who has previously purchased a few course modules, returns to
the website. They go to the course page's buy tab, where they see
their previously purchased modules w/ seat counts. User can adjust the
slider upwards to buy more seats. They cannot lower the number of
seats. The user can add additional modules to the course. They cannot
remove existing modules. The slider shows the amount they must pay,
taking into account the amount they've already paid. The users checks
out. The backend should validate all of these numbers are correct when
charging. On successful payment, the user's course on edX is updated
with new content, modules, and maximum seats.

## Open Questions

- Do we need to do anything different with analytics when upgrading existing seat counts?
- How long does it take (on average/95% percentile) to create CCXs via the API?

## CCXCon

The CCXCon work is fairly straight forward. We need to add an
additional endpoint which supports `PUT`, passing along the CCX id,
and updates the corresponding ccx. _Technical Note_: the underlying
edX API only supports `PATCH`, so we'll have to submit this as a 
`PATCH`, but we can still pass the full object.


We do have to ensure the existing API sends back the CCXCon ID in the
create request. Without this, we'll create duplicate CCXs, which edx
[doesn't yet support](https://github.com/mitocw/edx-platform/pull/182).
Even when we do support multiple CCXs, accidental duplications will
not be desireable.

### CCXCon Timeouts & Course Ids.

There is a concern with timeouts in heroku. Heroku gives us a 30
second budget to complete requests. These requests will start from
Teachers' Portal. Given we're making API calls to stripe, that gives
us something like a 25 second budget for CCXCon. edX CCX creation
takes several seconds (10+?). If we exceed this budget, we don't get
the ccx id back to Teacher's Portal. This means Teacher's Portal will
be unable to submit updates to this order, as we won't know which ccx
to update.

One fix to this is to have CCXCon query for the existence of a CCX
that already exists for a user/course combo. Due to how users are
likely to purchase courses (i.e. a single user will purchase multiple
versions of a CCX), there will not be a unique way to identify these
CCXs on edX.

To address this, we will need to create a unique field on edX which is
queryable through the API. We can use the id of the User<=>Course row
on TP (discussed below) to ensure there is a consistent and unique id
mapping a User<=>Course pair to an edX CCX. Before creating a new CCX,
we'll query for this id to determine whether the action is an update
or a create.

The above unique id solution also allows us to offload the course
creation into an async queue. This would allow ccxcon to wait for
longer than the 25 second budget. Unfortunately, this would also push
TP to be async in this request, which means the UI will need to query
for job state. This should live inside CCXCon and be powered by
[celery's result API](https://celery.readthedocs.org/en/stable/getting-started/first-steps-with-celery.html#keeping-results)
with an associated API for
[querying job status](https://www.reddit.com/r/django/comments/1wx587/how_do_i_return_the_result_of_a_celery_task_to/cf6nddw). This
change could require setting up a non-redis backend store as we likely
will need more durability guarantees. To handle this case seems like a
fair amount of work, but makes the system more resilient. We need a
bit more real-world timing around copying CCXs to know how likely this
problem is to occur.

If this fails, how can the TP rectify itself? Given that we will have
a mapping of User<=>Course pairs, we should be able to write a groomer
script which will look for the pairs which do not have a backing CCX
id and request it from a yet-to-be-written CCXCon API.

## TP API

We need to know if a particular user has purchased a particular
course. To store this, we'll need a join table between users and
courses that exists outside of `OrderLine`s to store their CCX
id. `OrderLine` is insufficient, as they might have multiple orders
for a single course (e.g. purchase once, then buy more seats at a future
time). On this Course<=>User mapping, we can store a field referencing
the modules they've purchased (which might change over time) and the
seat counts.

We'll also need to expand the validation around pricing to account for
already purchased goods.

### Extra API or merge in purchase info?

There are two options to get the "has the user purchased this course?"
data into the frontend. One would be to add an additional API to get
the list of purchased courses. The other option is to merge "has this
user purchased this?" data into the payload.

The advantage of the merge option is that there is less work involved
in the javascript. We won't have to make additional API calls and the
data will be right there for our users. The big downside to this
approach is that we lose the ability to cache responses, as there will
be user-specific data in them.

As we are currently focused on optimizing time to delivery, *I'm
advocating for the merge option*. We should be able to back this out
into a separate API with minimal fuss (given the async support for
redux stores) if our payloads start to warrant it.

## TP UI

Given there is a requirement that a person could purchase multiple
CCXs (for instance, one for a fall term and another for a spring
term) the course update UI we have now doesn't work.

Instead, we should detect if a user has purchased a CCX. If they have,
we'll provide a bit of text that says something to the effect of "It
looks like you've already purchased this course. If you'd like to add
seats to it, go here". This will link off to an admin page described
below.

The existing cart scenario will change a bit. You can add a course as
you do now by selecting modules and seats, then clicking 'add to
cart'. The form would then reset. If you click add to cart again,
we'll create another entry (possibly with a different module/seat
configuration).

If you view your cart, there will be an edit button on each entry
there. Clicking it will take you to the course detail page for that
course with the buy tab preselected and auto-populated with the info
for that cart item. You can select more modules or add / reduce seats
and click the 'update' button. Clicking the update button will reset
the form again, just like the add to cart did above. In this edit
view, the "it looks like you've already bought this course" link won't
show up, as it might confuse people between cart editing and existing
purchased course editing.

If the user wants to edit their existing course (clicking on the
aforementioned button), they'll be taken to a course listing view
similar to the instructor view on
[invisionapp](https://projects.invisionapp.com/share/Y84OLUER6#/screens/114236139). Here,
they can adjust their seat counts or module selection. They won't be
able to reduce the number of seats they've purchased, only
increase. They won't be able to remove already purchased modules, only
add more. The UI should enforce these constraints by disabling as
relevant. Making changes here will add to the cart, like the existing
checkout flow.

Unsupported changes like refunds, removing course modules, removing
seats, etc will all be handled via zendesk support tickets.

## Questions

Q: How does the user delete modules or lower their max seats?
A: They contact support via the zendesk widget.

Q: Do we support refunds?
A: Not in the UI. Contact support via the zendesk widget.

Q: Do we support bulk editing of already purchased modules (eg +10 seats to 10 different courses)?
A: Not yet. Maybe in the future.
