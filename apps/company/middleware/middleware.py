from threading import local

from django.utils.deprecation import MiddlewareMixin

from ..models import Company

_thread_locals = local()


def get_current_company(request):
    company = getattr(_thread_locals, "company", None)

    if not company:
        company_id = request.session.get("company_id")
        if company_id:
            try:
                company = Company.objects.get(id=company_id)
                _thread_locals.company = company
            except Company.DoesNotExist:
                company = None

    return company


class CompanyMiddleware(MiddlewareMixin):
    def __call__(self, request):
        company_id = self.get_company_from_request(request)
        print(f"Company ID from request: {company_id}")

        if company_id:
            try:
                company = Company.objects.get(id=company_id)
                _thread_locals.company = company
                print(f"Company found: {company}")
            except Company.DoesNotExist:
                _thread_locals.company = None
                print("Company does not exist.")
        else:
            _thread_locals.company = None
            print("No company ID found in request.")

        response = self.get_response(request)
        return response

    def get_company_from_request(self, request):
        print(f"Request META: {request.META}")
        company_id = request.META.get("HTTP_X_COMPANY_ID")
        print(f"Company ID from header: {company_id}")

        if not company_id:
            company_id = request.session.get("company_id")
            print(f"Company ID from session: {company_id}")

        if not company_id:
            company_id = request.GET.get("company_id")
            print(f"Company ID from URL: {company_id}")

        return company_id
