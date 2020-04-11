from twilio.rest import Client

account_sid="AC3f1eb73d06dbd7a2bba7708f5c159f82"
auth_token='776588f1ecc65e05fca779cdb50e6081'

client= Client(account_sid,auth_token)

client.messages.create(
    to='+917566111208',
    from_='+12029526639',
    body='This is demo'
)