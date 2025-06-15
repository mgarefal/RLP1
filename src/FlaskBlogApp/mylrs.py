import uuid
from flask import (render_template,
                   redirect,
                   url_for,
                   request,
                   flash, 
                   abort,
                   Response,
                   session)


import FlaskBlogApp.lrs_properties as lrsproperties
from tincan import (
    RemoteLRS,
    Statement,
    Agent,
    Verb,
    Activity,
    Context,
    LanguageMap,
    ActivityDefinition,
    StateDocument,
    Extensions
)

def SendStatement(UserName, UserEmail, myAction, myActivity, PIN_Status=None,LRS_session_id=None,Remote_Lab=None,statetmentType=None,sketchCreated=None,sketchUse=None,compileResult=None,compileError=None, uploadResult=None,uploadError=None,sketchTitle=None, StatusReport=None,ActivityDesc=None,ActivityResult=None, ActivityPercent=None,ResultReason=None,AIPrompt=None, AIReply=None,ActivityMetadata=None):

    # Construct an LRS
    lrs = RemoteLRS(
        version=lrsproperties.version,
        endpoint=lrsproperties.endpoint,
        username=lrsproperties.username,
        password=lrsproperties.password,
    )
    
    # Get the session ID from Flask session (or generate one if not present)
    #LRS_session_id = session.get('LRS_session_id', str(uuid.uuid4()))  # Retrieve from session or generate new
    
    # Construct the actor of the statement
    actor = Agent(
        name=UserName,
        mbox='mailto:' + UserEmail,
    )

    # Construct the verb of the statement
    verb = Verb(
        id='http://garefalakis.eu/expapi/verbs/' + myAction,
        display=LanguageMap({'en-US': str(myAction)}),
    )

    # Construct the object of the statement
    object = Activity(
        id='http://garefalakis.eu/' + myActivity,
        definition=ActivityDefinition(
            name=LanguageMap({'en-US': str(myActivity)}),
            description=LanguageMap({'en-US': 'Use of ' + str(myActivity)}),
        ),
    )

    # Construct a context for the statement including session ID
    context = Context(
        registration=uuid.uuid4(),
        instructor=Agent(
            name='Spiros Panagiotakis',
            mbox='mailto:spanag@elmepa.gr'
        ),
        extensions=Extensions({
            'https://garefalakis.eu/extensions/session-id': LRS_session_id,
            'https://garefalakis.eu/extensions/pin_status': PIN_Status,
            'https://garefalakis.eu/extensions/Remote_Lab': Remote_Lab,
            'https://garefalakis.eu/extensions/statetment_Type': statetmentType,
            'https://garefalakis.eu/extensions/sketchCreated': sketchCreated,
            'https://garefalakis.eu/extensions/sketchUse': sketchUse,
            'https://garefalakis.eu/extensions/compileResult': compileResult,
            'https://garefalakis.eu/extensions/uploadResult': uploadResult,
            'https://garefalakis.eu/extensions/sketchTitle': sketchTitle,
            'https://garefalakis.eu/extensions/compileError': compileError,
            'https://garefalakis.eu/extensions/uploadError': uploadError,
            'https://garefalakis.eu/extensions/StatusReport': StatusReport,
            'https://garefalakis.eu/extensions/ActivityTitle': myActivity,
            'https://garefalakis.eu/extensions/ActivityDesc': ActivityDesc,
            'https://garefalakis.eu/extensions/passed': ActivityResult,
            'https://garefalakis.eu/extensions/percentage_correct': ActivityPercent,
            'https://garefalakis.eu/extensions/result_reason': ResultReason,
            'https://garefalakis.eu/extensions/AIPrompt': AIPrompt,
            'https://garefalakis.eu/extensions/AIReply': AIReply,
            'https://garefalakis.eu/extensions/ActivityMetadata': ActivityMetadata

        }),
    )

    # Construct the actual statement
    statement = Statement(
        actor=actor,
        verb=verb,
        object=object,
        context=context,
    )

    # Save the statement to the LRS and store the response in 'response'
    print("Saving the Statement...")
    response = lrs.save_statement(statement)

    if not response:
        raise ValueError("Statement failed to save")

    # Retrieve the statement from the LRS using the ID returned in the response
    print("Now, retrieving statement...")
    response = lrs.retrieve_statement(response.content.id)

    if not response.success:
        raise ValueError("Statement could not be retrieved")
    print("...done")

    # Construct a new Statement from the retrieved statement data
    print("Constructing new Statement from retrieved statement data...")
    ret_statement = response.content
    print("...done")

    # Save both the original and the retrieved statements
    print("Saving both Statements")
    response = lrs.save_statements([statement, ret_statement])

    if not response:
        raise ValueError("Statements failed to save")
    print("...done")

    # Query statements (optional)
    query = {
        "agent": actor,
        "verb": verb,
        "activity": object,
        "related_activities": True,
        "related_agents": True,
        "limit": 2,
    }

    print("Querying statements...")
    response = lrs.query_statements(query)

    if not response:
        raise ValueError("Statements could not be queried")
    print("...done")

    # Save a state document (optional)
    state_document = StateDocument(
        activity=object,
        agent=actor,
        id='stateDoc',
        content=bytearray('stateDocValue', encoding='utf-8'),
    )

    print("Saving state document...")
    response = lrs.save_state(state_document)

    if not response.success:
        raise ValueError("Could not save state document")
    print("...done")
