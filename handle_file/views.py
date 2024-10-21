import pandas as pd
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from rest_framework import status
from .forms import FileUploadForm
from django.shortcuts import render
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

class FileUploadAPIView(APIView):
    def get(self, request):
        form = FileUploadForm()
        return render(request, 'upload.html', {'form': form})

    def post(self, request):
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            summary_data = self.handle_uploaded_file(file) 
            self.send_summary_email(summary_data) 
            return render(request, 'success.html', summary_data) 

        return Response({'error': 'Invalid form submission'}, status=status.HTTP_400_BAD_REQUEST)

    def handle_uploaded_file(self, f):
        df = pd.read_excel(f) if f.name.endswith('.xlsx') else pd.read_csv(f)
        df.rename(columns={'Cust State': 'Cust_State', 'Cust Pin': 'Cust_Pin'}, inplace=True)

        total_customers = len(df)
        average_dpd = df['DPD'].mean()
        customer_states = df['Cust_State'].nunique()

        summary_data = {
            'total_customers': total_customers,
            'average_dpd': average_dpd,
            'unique_customer_states': customer_states,
            'sample_data': df[['Cust_State', 'Cust_Pin', 'DPD']].to_dict(orient='records')
        }

        return summary_data



    def send_summary_email(self, summary_data):
        subject = "Python Assignment - Aditya Kumar"

        email_html_content = render_to_string('success.html', {
        'total_customers': summary_data['total_customers'],
        'average_dpd': summary_data['average_dpd'],
        'unique_customer_states': summary_data['unique_customer_states'],
        'sample_data': summary_data['sample_data']
    })

        email = EmailMessage(
        subject=subject,
        body=email_html_content,
        from_email=settings.EMAIL_HOST_USER,
        to=['tech@themedius.ai'],
    )

        email.content_subtype = "html"  
        email.send(fail_silently=False)
