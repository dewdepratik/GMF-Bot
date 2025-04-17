import os
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import uvicorn
from dotenv import load_dotenv
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.caml.query import CamlQuery

# Load environment variables from .env file
load_dotenv()

# Create FastAPI app
app = FastAPI(title="SharePoint Events API")

# Environment variables for SharePoint credentials
SHAREPOINT_SITE_URL = "https://sophtimize.sharepoint.com/sites/GMFDemo"
SHAREPOINT_USERNAME = "dhiraj.nehate@sophtimize.com"
SHAREPOINT_PASSWORD = "DnSph@2023" 

# Models
class Event(BaseModel):
    id: int
    title: str
    start_date: datetime
    end_date: Optional[datetime] = None
    location: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    all_day: Optional[bool] = False

class EventFilter(BaseModel):
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    category: Optional[str] = None

# SharePoint connection helper
def get_sharepoint_context():
    if not all([SHAREPOINT_SITE_URL, SHAREPOINT_USERNAME, SHAREPOINT_PASSWORD]):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SharePoint credentials not configured"
        )
    
    try:
        credentials = UserCredential(SHAREPOINT_USERNAME, SHAREPOINT_PASSWORD)
        ctx = ClientContext(SHAREPOINT_SITE_URL).with_credentials(credentials)
        return ctx
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect to SharePoint: {str(e)}"
        )


# @app.get("/events", response_model=List[Event], tags=["Events"])
def get_events(
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    category: Optional[str] = None
):
    """
    Get events from SharePoint with optional filtering by date range and category
    """
    ctx = get_sharepoint_context()
    
    try:
        # Get the events list
        events_list = ctx.web.lists.get_by_title("Events")
        
        # Build CAML query based on filters
        caml_query = CamlQuery()
        query_text = """<View><Query>"""
        
        # Add where clause if filters are provided
        where_conditions = []
        
        if from_date:
            where_conditions.append(
                f"""<Geq><FieldRef Name='EventDate' /><Value Type='DateTime'>{from_date.strftime('%Y-%m-%dT%H:%M:%SZ')}</Value></Geq>"""
            )
        
        if to_date:
            where_conditions.append(
                f"""<Leq><FieldRef Name='EventDate' /><Value Type='DateTime'>{to_date.strftime('%Y-%m-%dT%H:%M:%SZ')}</Value></Leq>"""
            )
            
        if category:
            where_conditions.append(
                f"""<Eq><FieldRef Name='Category' /><Value Type='Text'>{category}</Value></Eq>"""
            )
            
        if where_conditions:
            query_text += "<Where>"
            if len(where_conditions) > 1:
                query_text += "<And>"
                
            for condition in where_conditions:
                query_text += condition
                
            if len(where_conditions) > 1:
                query_text += "</And>"
                
            query_text += "</Where>"
            
        query_text += """</Query><ViewFields>
            <FieldRef Name='ID' />
            <FieldRef Name='Title' />
            <FieldRef Name='EventDate' />
            <FieldRef Name='EndDate' />
            <FieldRef Name='Location' />
            <FieldRef Name='Description' />
            <FieldRef Name='Category' />
            <FieldRef Name='fAllDayEvent' />
        </ViewFields></View>"""
        
        caml_query.ViewXml = query_text
        
        # Execute the query
        items = events_list.get_items(caml_query)
        ctx.load(items)
        ctx.execute_query()
        
        # Convert SharePoint list items to Event model
        events = []
        for item in items:
            properties = item.properties
            event = Event(
                id=properties.get('ID', 0),
                title=properties.get('Title', ''),
                start_date=properties.get('EventDate'),
                end_date=properties.get('EndDate'),
                location=properties.get('Location', ''),
                description=properties.get('Description', ''),
                category=properties.get('Category', ''),
                all_day=properties.get('fAllDayEvent', False)
            )
            events.append(event)
        print("me call zali re",events) 
        return events
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching events: {str(e)}"
       )

# # Run the application
# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)