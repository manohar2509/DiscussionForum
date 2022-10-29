from django.urls import path
from .views import AddDiscussion,GetDiscussions,UpdateDiscussion,DeleteDiscussion,GetDiscussionsByTag,GetDiscussionsByDate,GetDiscussionsByText
urlpatterns = [
    path('adddiscussion/',AddDiscussion.as_view(),name='adddiscussion'),
    path('getdiscussions/',GetDiscussions.as_view(),name='getdiscussions'),
    path('updatediscussion/',UpdateDiscussion.as_view(),name='updatediscussion'),
    path('deletediscussion/',DeleteDiscussion.as_view(),name='deletediscussion'),
    path('getdiscussionsbytag/',GetDiscussionsByTag.as_view(),name='getdiscussionsbytag'),
    path('getdiscussionsbydate/',GetDiscussionsByDate.as_view(),name='getdiscussionsbydate'),
    path('getdiscussionsbytext/',GetDiscussionsByText.as_view(),name='getdiscussionsbytext'),
]

