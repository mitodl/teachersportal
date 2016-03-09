# CCXCon Setup

## Setting up Docker

First, you need a working
CCXCon. [This guide](https://github.com/mitodl/ccxcon/blob/master/docs/ccxcon_edx_conf.md)
should help there.

To get teachersportal (TP) to integrate with this service, you should
run your TP a little differently, so that it's aware of the existing
ccxcon.

```sh
docker-compose -f docker-compose.yml \
    -f docker-compose.integration.yml \
    up web_integration watch
```

From here, TP will be aware of ccxcon at localhost.daplie.com, which
will have valid SSL certificates (which are required for oauth2).

## Setting up webhooks.

Next, you'll need to create a webhook on ccxcon.

1. Go to the [webhook add page](https://localhost.daplie.com:8077/admin/webhooks/webhook/add/)
2. Enter the URL of your TP. You can find this by finding the IP here.

```
docker inspect `docker ps | grep teachersportal_web_integration | awk {'print $1'}` | grep -i ipaddress
```

For me, that was 172.17.0.6, so that'll be your base url. It might be
different between docker runs, so you may have to edit this in the
future.

For the URL, put in http://172.17.0.6:8075/api/v1/webhooks/ccxcon/ (or
replace the IP with whatever your API server was listed at).

3. Copy the secret. You'll need that later.
4. Click save.

You might consider adding another webhook for http://requestb.in/
which can validate that the webhooks are working. You get to see http
requests going in realtime. Not required, but helpful to validate.


## OAuth Client

Now we need to add an oauth client so TP can speak to CCXCon.

1. Go to the [create oauth application page](https://localhost.daplie.com:8077/admin/oauth2_provider/application/add/)
2. Pick some user. I picked my super user.
3. Client type: confidential
4. Authorization grant type: client credentials
5. Give it a name like "teachers portal"
6. Copy the client id and client secret for later use.
6. Save.

## .env file

Edit the `.env` file in the root of your TP repo. There's a
`.env.sample` if you want a guide to go on. It should look like below:

```
CCXCON_API=https://localhost.daplie.com:8077/api/
CCXCON_OAUTH_CLIENT_ID=
CCXCON_OAUTH_CLIENT_SECRET=
CCXCON_WEBHOOKS_SECRET=
```

You'll need to use the client id, client secret, and webhook secret
you copied from the previous steps in here next to their respective
values.

## Testing it.

In CCXCon type what I've typed below. This assumes that you have
courses in your ccxcon. If you don't, generate some with the
management command or hook it up to a working edx instance.

```
docker-compose run web ./manage.py shell
from courses.models import Course
Course.objects.all()[0].save()
```

You should have data inside your TP now (and on the requestb.in
service if you did that step).
