# django
from rest_framework import serializers, status
from rest_framework.exceptions import NotFound
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# local django
from authentication.serializers import UserUpdateSerializer
from profile.models import Profile
from profile.renderers import ProfileJSONRenderer
from profile.serializers import ProfileSerializer


class ProfileRetrieveAPIView(RetrieveAPIView):
    permission_classes = (AllowAny,)
    queryset = Profile.objects.select_related('user')
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = ProfileSerializer
    user_serializer_class = UserUpdateSerializer

    def get(self, request, *args, **kwargs):
        # Try to retrieve the requested profile and throw an exception if the
        # profile could not be found.
        try:
            profile = self.queryset.get(user__username=kwargs['username'])
        except Profile.DoesNotExist:
            raise NotFound('A profile with ' + kwargs['username'] + ' username does not exist.')

        serializer = self.serializer_class(profile, context={
            'request': request
        })

        user_serializer = self.user_serializer_class(request.user)
        print(serializer.data)
        new_data = {
            'profile': serializer.data,
            'user': user_serializer.data
        }

        return Response(new_data, status=status.HTTP_200_OK)


class ProfileFollowAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = ProfileSerializer

    def delete(self, request, username=None):
        follower = self.request.user.profile

        try:
            followee = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            raise NotFound('A profile with this username was not found')

        follower.unfollow(followee)

        serializer = self.serializer_class(followee, context={
            'request': request
        })

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, username=None):
        follower = self.request.user.profile

        try:
            followee = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            raise NotFound(' A profile with this username was not found.')

        if follower.pk is followee.pk:
            raise serializers.ValidationError('You can\'t follow yourself')

        follower.follow(followee)

        serializer = self.serializer_class(followee, context={
            'request': request
        })

        return Response(serializer.data, status=status.HTTP_201_CREATED)