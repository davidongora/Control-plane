import { HttpInterceptorFn } from '@angular/common/http';

function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) {
    return parts.pop()?.split(';').shift() || null;
  }
  return null;
}

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const csrfToken = getCookie('csrftoken');
  
  const modifiedReq = req.clone({
    withCredentials: true,
    setHeaders: csrfToken ? {
      'X-CSRFToken': csrfToken
    } : {}
  });
  
  return next(modifiedReq);
};
