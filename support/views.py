# support/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Ticket, Message
from .serializers import TicketSerializer, MessageSerializer, AdminTicketSerializer
from users.models import User  # Assurez-vous que User est importé
from core.utils import send_notification_to_user



class TicketCreateView(generics.CreateAPIView):
    """
    Permet à un utilisateur authentifié de créer un nouveau ticket de support.
    """
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        ticket = serializer.save(user=self.request.user)
        send_notification_to_user(
            self.request.user,
            f"Votre ticket de support '{ticket.subject}' a été créé avec succès. Un agent vous contactera bientôt.",
            notification_type='support_update',
            ticket_obj=ticket
        )


class UserTicketListView(generics.ListAPIView):
    """
    Permet à un utilisateur authentifié de lister tous ses tickets de support.
    """
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Ticket.objects.filter(user=self.request.user).order_by('-created_at')


class UserTicketDetailView(generics.RetrieveAPIView):
    """
    Permet à un utilisateur authentifié de voir les détails d'un de ses tickets.
    """
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # S'assure que l'utilisateur ne peut voir que ses propres tickets
        return Ticket.objects.filter(user=self.request.user)


class UserMessageCreateView(generics.CreateAPIView):
    """
    Permet à un utilisateur d'ajouter un message à un de ses tickets ouverts/en cours.
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        ticket_id = self.kwargs.get('pk')
        ticket = get_object_or_404(Ticket, id=ticket_id, user=self.request.user)

        if ticket.status in ['closed', 'resolved']:
            raise permissions.ValidationError("Impossible d'ajouter un message à un ticket fermé ou résolu.")

        message = serializer.save(ticket=ticket, sender=self.request.user)
        # Envoyer une notification à l'administrateur ou aux agents de support
        # (Dans un vrai système, cela irait à un groupe d'admins ou à une file d'attente)
        send_notification_to_user(
            ticket.user,  # Envoyer aussi à l'utilisateur lui-même une confirmation
            f"Votre message a été ajouté au ticket '{ticket.subject}'.",
            notification_type='support_update',
            ticket_obj=ticket
        )
        # Idéalement, notifier un admin que le ticket a une nouvelle réponse
        # send_notification_to_admin(f"Nouveau message sur ticket #{ticket.id}")



class AdminTicketListView(generics.ListAPIView):
    """
    Permet aux administrateurs de lister tous les tickets de support.
    """
    queryset = Ticket.objects.all().order_by('-created_at')
    serializer_class = AdminTicketSerializer
    permission_classes = [permissions.IsAdminUser]


class AdminTicketDetailView(generics.RetrieveUpdateAPIView):
    """
    Permet aux administrateurs de voir les détails et de mettre à jour le statut/priorité d'un ticket.
    """
    queryset = Ticket.objects.all()
    serializer_class = AdminTicketSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_update(self, serializer):
        ticket = serializer.save()
        # Envoyer une notification à l'utilisateur si le statut du ticket est modifié
        if 'status' in serializer.validated_data:
            send_notification_to_user(
                ticket.user,
                f"Le statut de votre ticket '{ticket.subject}' a été mis à jour à '{ticket.get_status_display()}'.",
                notification_type='support_update',
                ticket_obj=ticket
            )


class AdminMessageCreateView(generics.CreateAPIView):
    """
    Permet à un administrateur d'ajouter un message à un ticket.
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        ticket_id = self.kwargs.get('pk')
        ticket = get_object_or_404(Ticket, id=ticket_id)

        message = serializer.save(ticket=ticket, sender=self.request.user)
        # Envoyer une notification à l'utilisateur du ticket
        send_notification_to_user(
            ticket.user,
            f"Une réponse a été ajoutée à votre ticket '{ticket.subject}'.",
            notification_type='support_update',
            ticket_obj=ticket
        )
