from twilio.rest import Client

class TwilioException(Exception):
    pass

class Twilio:

    def __init__(self, accountSID: str, authToken: str, fromNumber: str):
        self.accountSID = accountSID
        self.authToken = authToken
        self.fromNumber = f"+{fromNumber}"

        self._createClient()
        
    def _createClient(self) -> None:
        self.client = Client(self.accountSID, self.authToken)


    def sendSMS(self, toNumber: str, msg: str) -> None:
        try:
            self.client.messages.create(
                                  body=msg,
                                  from_=self.fromNumber,
                                  to=f"+{toNumber}"
                                )
            
        except Exception as e:
            raise TwilioException(f"{e.msg}") from None
       
