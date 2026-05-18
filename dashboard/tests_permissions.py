from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Organization, OrganizationMember, Cliente, Categoria, Dashboard, DeletionRequest

class PermissionTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create users
        self.admin_user = User.objects.create_user(username='admin', password='password')
        self.member_user = User.objects.create_user(username='member', password='password')
        
        # Create organization
        # Note: We must use allowed names "Principal" or "Modelos"
        self.org = Organization.objects.create(name='Principal', created_by=self.admin_user)
        
        # Assign roles
        OrganizationMember.objects.create(
            organization=self.org,
            user=self.admin_user,
            role=OrganizationMember.Role.ADMINISTRADOR
        )
        OrganizationMember.objects.create(
            organization=self.org,
            user=self.member_user,
            role=OrganizationMember.Role.MEMBRO
        )
        
        # Create some content
        self.cliente = Cliente.objects.create(organization=self.org, name='Test Cliente')
        self.categoria = Categoria.objects.create(organization=self.org, name='Test Categoria')
        self.dashboard = Dashboard.objects.create(
            organization=self.org,
            client=self.cliente,
            title='Test Dashboard',
            image='test.png', # Placeholder
            json='test.json'  # Placeholder
        )

    def test_admin_can_delete_directly(self):
        self.client.login(username='admin', password='password')
        session = self.client.session
        session['active_org_id'] = self.org.id
        session.save()
        
        response = self.client.post(reverse('deletar_cliente', args=(self.cliente.slug,)))
        self.assertFalse(Cliente.objects.filter(id=self.cliente.id).exists())
        self.assertEqual(response.status_code, 302)

    def test_member_cannot_delete_but_creates_request(self):
        self.client.login(username='member', password='password')
        session = self.client.session
        session['active_org_id'] = self.org.id
        session.save()
        
        response = self.client.post(reverse('deletar_cliente', args=(self.cliente.slug,)), {'reason': 'Quero apagar'})
        
        # Cliente should still exist
        self.assertTrue(Cliente.objects.filter(id=self.cliente.id).exists())
        
        # DeletionRequest should be created
        self.assertTrue(DeletionRequest.objects.filter(
            organization=self.org,
            requested_by=self.member_user,
            content_type=DeletionRequest.ContentType.CLIENTE,
            object_id=self.cliente.id
        ).exists())
        self.assertEqual(response.status_code, 302)

    def test_admin_can_approve_request(self):
        # Create a request first
        req = DeletionRequest.objects.create(
            organization=self.org,
            requested_by=self.member_user,
            content_type=DeletionRequest.ContentType.CLIENTE,
            object_id=self.cliente.id,
            object_name=self.cliente.name
        )
        
        self.client.login(username='admin', password='password')
        session = self.client.session
        session['active_org_id'] = self.org.id
        session.save()
        
        response = self.client.post(reverse('revisar_solicitacao', args=(req.id,)), {
            'action': 'approve',
            'notes': 'Ok, aprovado'
        })
        
        # Cliente should be deleted
        self.assertFalse(Cliente.objects.filter(id=self.cliente.id).exists())
        
        # Request status should be APPROVED
        req.refresh_from_db()
        self.assertEqual(req.status, DeletionRequest.Status.APPROVED)
        self.assertEqual(req.reviewed_by, self.admin_user)

    def test_organization_creation_restriction(self):
        # Admin trying to create another org
        with self.assertRaises(Exception): # ValidationError will be raised in save()
             Organization.objects.create(name='Outra Org', created_by=self.admin_user)
        
    def test_organization_deletion_restriction(self):
        # Admin trying to delete the org
        with self.assertRaises(Exception): # ValidationError will be raised in delete()
            self.org.delete()
