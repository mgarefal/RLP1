# An example script showing the functionality of the TinCanPython Library

import uuid
from flask import (render_template,
                   redirect,
                   url_for,
                   request,
                   flash, 
                   abort,
                   Response)


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

def SendStatement(UserName, UserEmail, myAction, myActivity ): 
    # construct an LRS
    #print("constructing the LRS...")
    #flash("constructing the LRS...")
    lrs = RemoteLRS(
        version=lrsproperties.version,
        endpoint=lrsproperties.endpoint,
        username=lrsproperties.username,
        password=lrsproperties.password,
    )
    #print("...done")

    # construct the actor of the statement
    #print("constructing the Actor...")
    actor = Agent(
        name=UserName,
        mbox='mailto:'+ UserEmail ,
    )
    #print("...done")

    # construct the verb of the statement
    #print("constructing the Verb...")
    verb = Verb(
        id='http://garefalakis.eu/expapi/verbs/' + myAction,
        display=LanguageMap({'en-US': str(myAction)}),
    )
    #print("...done")

    # construct the object of the statement
    #print("constructing the Object...")
    object = Activity(
        id='http://garefalakis.eu/'+ myActivity,
        definition=ActivityDefinition(
            name=LanguageMap({'en-US': str(myActivity)}),
            description=LanguageMap({'en-US': 'Use of ' + str(myActivity)}),
        ),
    )
    #print("...done")

    # construct a context for the statement
    #print("constructing the Context...")
    context = Context(
        registration=uuid.uuid4(),
        instructor=Agent(
            name='Spiros Panagiotakis',
            mbox='mailto:spanag@elmepa.gr'),
            extensions=Extensions({'https://garefalakis.eu/extensions/test':'test2','https://garefalakis.eu/extensions/test2':'test1'}),   
        

        # language='en-US',
    )
    #print("...done")

    # construct the actual statement
    #print("constructing the Statement...")
    statement = Statement(
        actor=actor,
        verb=verb,
        object=object,
        context=context,
    )
    #print("...done")

    # save our statement to the remote_lrs and store the response in 'response'
    print("saving the Statement...")
    response = lrs.save_statement(statement)

    if not response:
        raise ValueError("statement failed to save")
    #print("...done")

    # retrieve our statement from the remote_lrs using the id returned in the response
    print("Now, retrieving statement...")
    response = lrs.retrieve_statement(response.content.id)

    if not response.success:
        raise ValueError("statement could not be retrieved")
    print("...done")

    print("constructing new Statement from retrieved statement data...")
    ret_statement = response.content
    print("...done")

    # now, using our old statement and our returned statement, we can send multiple statements
    # note: these statements are logically identical, but are 2 separate objects
    print("saving both Statements")
    response = lrs.save_statements([statement, ret_statement])

    if not response:
        raise ValueError("statements failed to save")
    print("...done")

    # we can query our statements using an object
    # constructing the query object with common fields
    # note: more information about queries can be found in the API documentation:
    # docs/build/html/tincan.html#module-tincan.remote_lrs
    query = {
        "agent": actor,
        "verb": verb,
        "activity": object,
        "related_activities": True,
        "related_agents": True,
        "limit": 2,
    }

    print("querying statements...")
    response = lrs.query_statements(query)

    if not response:
       raise ValueError("statements could not be queried")
    print("...done")

    # now we will explore saving a document, e.g. a state document
    print("constructing a state document...")
    state_document = StateDocument(
        activity=object,
        agent=actor,
        id='stateDoc',
        content=bytearray('stateDocValue', encoding='utf-8'),
    )

    print("...done")
    print("saving state document...")
    response = lrs.save_state(state_document)

    if not response.success:
        raise ValueError("could not save state document")
    print("...done")

