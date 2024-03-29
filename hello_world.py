# -*- coding: utf-8 -*-

# This is a simple Hello World Alexa Skill, built using
# the implementation of handler classes approach in skill builder.
import logging
import requests
import time
from random import randint

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model.services.directive import (
    SendDirectiveRequest, Header, SpeakDirective)

from ask_sdk_model.ui import SimpleCard
from ask_sdk_model import Response

from ask_sdk_core.api_client import DefaultApiClient
from ask_sdk_core.skill_builder import CustomSkillBuilder

sb = CustomSkillBuilder(api_client=DefaultApiClient())

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


URL = 'http://35.197.194.231:5000/authenticate/'
headers = "Content-Type: application/json"


#globals for flow control
fact_number = None
fact_name = None
transaction_completed = False

def check_auth(json):
    r = requests.post(URL,
                  json = json, #{"source":"mary","target":"john", "value": 100},
                  headers = {"Content-Type": "application/json"})
    ans = r.json()
    if ans['auth'] == 1:
        return True
    
    return False
    
def check_values(json):
    r = requests.post(URL,
                  json = json, #{"source":"mary","target":"john", "value": 100},
                  headers = {"Content-Type": "application/json"})
    ans = r.json()
    return ans['value']
    
def _progressive_response_(handler_input, speech): 
    #Call Alexa Directive Service.
    requestEnvelope = handler_input.request_envelope
    directiveServiceClient = handler_input.service_client_factory.get_directive_service();
    requestId = requestEnvelope.request.request_id;
    endpoint = handler_input.request_envelope.context.system.api_endpoint
    accessToken = handler_input.request_envelope.context.system.api_access_token 
    directive = SendDirectiveRequest(
                header    = Header(requestId),
                directive = SpeakDirective(
                            speech = speech
              )
    )    
    #send directive
    return directiveServiceClient.enqueue(directive)

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "Welcome to the Capital One online payment! What can I help you today?"

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Hello World", speech_text)).set_should_end_session(
            False)
        return handler_input.response_builder.response



class HelloWorldIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("HelloWorldIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        #cash = handler_input["slots"]
        slots = handler_input.request_envelope.request.intent.slots
        global fact_number
        global fact_name
        fact_number = int(slots["cash"].value)
        fact_name = str(slots["person"].value).lower()
        
        speech_text = "Do you want to transfer " + str(fact_number) + " pounds to " + str(fact_name) + '?'
        
        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Hello World", speech_text)).set_should_end_session(
            False)
        return handler_input.response_builder.response
        
class YesTransactionIntentHandler(AbstractRequestHandler):
    """Handler for YesTransaction Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.YesIntent")(handler_input) and not transaction_completed

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots
        #request_envelope.request.intent.slots
        fact_operation = "transfer"

        payload = {"source": "mary",
                    "target": fact_name,
                    "value":fact_number,
                    "operation": fact_operation
        }

        start = time.time()
        now = time.time()
        auth = False
        
        while not auth and now-start < 60:
            auth = check_auth(payload)
            now = time.time()
            time.sleep(1)
        
        if auth:
            global transaction_completed
            transaction_completed = True
            speech_text = "The payment of "  + str(fact_number) + " pounds to " + fact_name + " was done succesfully! " + \
            "Would you like to add the transaction to Splitwise?"
        else:
            speech_text = "Transaction not authorized."

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Hello World", speech_text)).set_should_end_session(
            False)
        return handler_input.response_builder.response
        

class NoTransactionIntentHandler(AbstractRequestHandler):
    """Handler for NoTransaction Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.NoIntent")(handler_input)

    def handle(self, handler_input):
        global transaction_completed
        if transaction_completed:
            speech_text = "Okay! I wont add the transaction to Splitwise"
            
            transaction_completed = False
            
        else:
            speech_text = "Operation canceled"

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Hello World", speech_text)).set_should_end_session(
            False)
        return handler_input.response_builder.response

class SplitwiseIntentHandler(AbstractRequestHandler):
    """Handler for Splitwise Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.YesIntent")(handler_input) and transaction_completed

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        speech_text = "Transaction added to your splitwise account!"
        
        global transaction_completed
        transaction_completed = False
        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Hello World", speech_text)).set_should_end_session(
            False)
        return handler_input.response_builder.response
        
        
class CreditScoreIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("CreditScoreIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        fact_operation = "credit_score"

        payload = {"source": "mary",
                    "target": "",
                    "value": 0,
                    "operation": fact_operation
        }

        creditscore_value = int(check_values(payload))

        speech_text = "Your credit score is " + str(creditscore_value) + "."

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Hello World", speech_text)).set_should_end_session(
            False)
        return handler_input.response_builder.response

class BalanceIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("BalanceIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        fact_operation = "balance"

        payload = {"source": "mary",
                    "target": "",
                    "value": 0,
                    "operation": fact_operation
        }
        
        balance_value = int(check_values(payload))
        speech_text = "Your balance is " + str(balance_value) + " pounds."

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Hello World", speech_text)).set_should_end_session(
            False)
        return handler_input.response_builder.response

class RewardPointsIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("RewardPointsIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        fact_operation = "reward_points"

        payload = {"source": "mary",
                    "target": "",
                    "value": 0,
                    "operation": fact_operation
        }
        
        rewardpoints_value = int(check_values(payload))

        speech_text = "You have "+ str(rewardpoints_value) + " reward points!"

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Hello World", speech_text)).set_should_end_session(
            False)
        return handler_input.response_builder.response


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "Goodbye!"

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Hello World", speech_text))
        return handler_input.response_builder.response


class FallbackIntentHandler(AbstractRequestHandler):
    """AMAZON.FallbackIntent is only available in en-US locale.
    This handler will not be triggered except in that locale,
    so it is safe to deploy on any locale.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = (
            "The Hello World skill can't help you with that.  "
            "You can say hello!!")
        reprompt = "You can say hello!!"
        handler_input.response_builder.speak(speech_text).ask(reprompt)
        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        return handler_input.response_builder.response


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Catch all exception handler, log exception and
    respond with custom message.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speech = "Sorry, there was some problem. Please try again!!"
        handler_input.response_builder.speak(speech).ask(speech)

        return handler_input.response_builder.response


sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelloWorldIntentHandler())
sb.add_request_handler(NoTransactionIntentHandler())
sb.add_request_handler(YesTransactionIntentHandler())
sb.add_request_handler(SplitwiseIntentHandler())
sb.add_request_handler(CreditScoreIntentHandler())
sb.add_request_handler(BalanceIntentHandler())
sb.add_request_handler(RewardPointsIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

handler = sb.lambda_handler()
