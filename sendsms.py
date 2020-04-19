from twilio.rest import Client

account_sid="THIS IS ALSO SECRET"
auth_token='THIS IS SECRET'

client= Client(account_sid,auth_token)

client.messages.create(
    to='MOBILE NUMbER',
    from_='SENDER MOB NO',
    body='This is demo'
)
