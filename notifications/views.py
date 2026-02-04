from rest_framework import generics, views, response, status
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer
from django.db.models import Q # Pour les requêtes complexes



class NotificationDetailView(generics.RetrieveAPIView):

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

class NotificationMarkAsReadView(views.APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id=None, *args, **kwargs):
        if notification_id:
            try:
                notification = Notification.objects.get(id=notification_id, user=request.user)
                notification.is_read = True
                notification.save()
                return response.Response({"message": "Notification marquée comme lue."}, status=status.HTTP_200_OK)
            except Notification.DoesNotExist:
                return response.Response({"error": "Notification non trouvée."}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Marquer toutes les notifications non lues de l'utilisateur comme lues
            Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
            return response.Response({"message": "Toutes les notifications ont été marquées comme lues."}, status=status.HTTP_200_OK)

class NotificationDeleteView(generics.DestroyAPIView):

    queryset = Notification.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return response.Response({"message": "Notification supprimée avec succès."}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return response.Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
