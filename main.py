from datetime import datetime, timedelta, timezone
import secrets

from fastapi import FastAPI, HTTPException, Request, Response
from jose import JWTError, jwt


app = FastAPI()
fake_db = []

## step of creating JWT { we require 3 alement : Payload + headrs+ Signature }
SECRET_KEY= "mysecret" 

def create_refresh_token(user_id: int) -> str:
    refresh_data = {
        "user_id": user_id,
        "jti": secrets.token_urlsafe(16),
    }
    refresh_expire = datetime.now(timezone.utc) + timedelta(days=7)
    refresh_data.update({"exp": int(refresh_expire.timestamp())})
    return jwt.encode(refresh_data, SECRET_KEY, algorithm="HS256")

#### once useer login we create 3 token and put it into the cookie, access token, refresh token and csrf token 
@app.get("/login-local")
def login_local(response :Response):
    

 ##### access_token ######
 # creating payload >>>> exp is one of the most important consept in JWT, 
    access_data = {
    "user_id":123
     }
    expire= datetime.now(timezone.utc) + timedelta(minutes=5)
    access_data.update({"exp": int(expire.timestamp())})
    access_token = jwt.encode(access_data,SECRET_KEY, algorithm="HS256") 

    

    #### refresh token###

    refresh_token = create_refresh_token(user_id=123)

    fake_db.append({
        "user_id":123,
        "refresh_token": refresh_token,
        "is_valid":True
    })
    print(fake_db)


    csrf_token = secrets.token_urlsafe(32)
    

### save tokens into Browser cookies ####


    response.set_cookie(
        key= "csrf_token",
        value=csrf_token
    )
    response.set_cookie(
        key= "access_token",
        value= access_token,
        httponly=True, ## prevent XSS atack 
        secure=False, ## only HHTPS accepts 
        samesite="lax" ## with this hacker won't be able to send the tokens to anothers website 
    )

    response.set_cookie(
        key ="refresh_token",
        value=refresh_token,
        httponly= True,
        secure=False,
        samesite="lax"
    )

    return {"massage":"logged in"}


@app.get("/profile_local") ## Server get cookies from Browser or request 
def profile_local(request :Request):
    token = request.cookies.get("access_token")

    if not token :
        raise HTTPException(status_code=401, detail="No Token ")
    try:
        decoded = jwt.decode (token, SECRET_KEY, algorithms=["HS256"])
        return decoded
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid Token")
    
    
### once the accesss tokek expires frontend will send the refresh token that stored in coolkies and get a new access token 
@app.get("/refresh")
def refresh(request :Request, response : Response):
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh Token")
    try:
        decoded = jwt.decode(refresh_token, SECRET_KEY, algorithms=["HS256"])
        user_id = decoded.get ("user_id")
        found = False
        for token in fake_db:
            if token["refresh_token"]==refresh_token:
                found = True
                if not token["is_valid"]:
                    ## revoke all session 
                    for t in fake_db:
                        if t["user_id"]==user_id:
                            t["is_valid"]= False
                    raise HTTPException(status_code=401, detail="Token reuse detected - sessions revoked")
                token["is_valid"] = False
                break

        if not found:
            raise HTTPException(status_code=401, detail="Refresh token not recognized")

## create a new token##
        new_date ={
        "user_id" : user_id
        }
        new_exp = datetime.now(timezone.utc) + timedelta(minutes= 5)
        new_date["exp"] =int(new_exp.timestamp())
        new_access_token =jwt.encode(new_date, SECRET_KEY,algorithm="HS256")

        ##create new refrsh_token 
        new_refresh_token = create_refresh_token(user_id=user_id)
        fake_db.append({
            "user_id":user_id,
            "refresh_token":new_refresh_token,
            "is_valid":True
        })
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            secure=False,
            samesite="lax"
        )

        response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly= True,
        secure=False,
        samesite="lax"
         )
        return{"message": "new access token created"}
    except JWTError:
      raise HTTPException(status_code=401, detail= "Invalid refresh token")
    

    
## sensitive request if has been sent backend must verify that the request is legit with csrf token, csrf_token and csrf_headers must be equal, 

@app.post("/update_profile")
def update_profile(request :Request):
    csrf_cookie = request.cookies.get("csrf_token")
    csrf_header = request.headers.get("X-CSRF-Token")
    if not csrf_cookie or not csrf_header or not secrets.compare_digest(csrf_cookie, csrf_header):
       raise HTTPException(status_code=403, detail="CSRF failed")

    return {"message":"update successfully"}
       
  
@app.get("/logout_local")
def logout_local(request : Request, response : Response):
    refresh_token= request.cookies.get("refresh_token")
    if refresh_token:
        for token in fake_db:
            if token["refresh_token"]==refresh_token:
                token["is_valid"]=False
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "logged out"}
