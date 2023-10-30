from app import app, db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from flask import request
from passlib.hash import pbkdf2_sha256
from flask_smorest import Blueprint, abort
from app.models import User, Blog, Comment, Like


# signup

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    

    user_check = db.session.query(User).filter(User.password == data["password"]).first()
    user_check1 = db.session.query(User).filter(User.username == data["username"]).first()
    
    if user_check or user_check1:
        return {"message": "error"}, 409
    
    else:
        
        
        user = User(
            email=data["email"],
            username=data["username"],
            password=pbkdf2_sha256.hash(data["password"]),
            photo='https://res.cloudinary.com/personal-cloud/image/upload/v1622763605/Sportify%20Images/photo_ebtvt9.png',)
        db.session.add(user)
        db.session.commit()

        return {"message": "User created successfully."}, 201
    


# update password

@app.route("/user/passwordUpdate", methods=["POST"])
def update_password():
    data = request.get_json()
    user = db.session.query(User).filter(User.id == data["id"]).first()
    if user:
        user.password = pbkdf2_sha256.hash(data["password"])
        db.session.add(user)
        db.session.commit()

    return {"message": "Password updated successfully!"}, 201


# update photo

@app.route("/user/photoUpdate", methods=["POST"])
def update_photo():
    data = request.get_json()
    user = db.session.query(User).filter(User.id == data["id"]).first()
    if user:
        user.photo = data["photo"]
        db.session.add(user)
        db.session.commit()

    return {"message": "Photo updated successfully!"}, 201


# get profile photo

@app.route("/user/getPhoto/<int:id>", methods=["GET"])
def get_photo(id):

    user = db.session.query(User).filter(User.id == id).first()
    if user:

        return {"data": user.photo}, 200


# login

@app.route("/loginUser", methods=["POST"])
def loginUser():
    data = request.get_json()

    user = db.session.query(User).filter(
        User.username == data["username"]).first()

    if user and pbkdf2_sha256.verify(data["password"], user.password):
        access_token = create_access_token(identity=user.id)
        return {"user": user.to_dict(), "access_token": access_token}, 200

    return {"message": "Invalid credentials"}, 401


# create blog

@app.route("/create", methods=["POST"])
def create_blog():
    data = request.get_json()
    blog = Blog(title=data['title'], body=data['body'],
                user_id=data['author'], image=data['image'])
    db.session.add(blog)
    db.session.commit()

    return {"message": "Blog created succesfully!"}, 201


# get all blogs

@app.route("/blogs", methods=["GET"])
def get_blogs():

    try:

        blogs = []
        result = db.session.query(Blog, User).join(
            User).order_by(Blog.id).all()

        for blog, user in result:
            blogs.append({
                "title": blog.title,
                "body": blog.body,
                "author": user.username,
                "id": blog.id,
                "image": blog.image
            }
            )

        return {"blogs": blogs}, 200

    except:
        abort(404, message="Blogs not found.")


# get  blog by id

@app.route("/blog/<int:id>", methods=["GET"])
def get_blog(id):

    try:

        result = db.session.query(Blog, User).join(
            User).filter(Blog.id == id).all()

        for b, u in result:

            blog_result = {
                "title": b.title,
                "body": b.body,
                "author": u.username,
                "id": b.id,
                "image": b.image,


            }

        return {**blog_result}, 200

    except:

        abort(404, message="Blogs not found.")


# show all users

@app.route("/allusers")
def allusers():

    try:
        users = db.session.query(User).all()

        return {"users": [user.to_dict() for user in users]}, 200

    except:
        return {"message": "There are no users"}, 404


# update a blog
@app.route("/blog/edit/<int:id>", methods=["PUT"])
def update_blog(id):
    data = request.get_json()
    try:

        newBlog = db.session.query(Blog).filter(Blog.id == id).first()
        newBlog.title = data['title']
        newBlog.body = data['body']
        newBlog.image = data['image']
        db.session.add(newBlog)
        db.session.commit()

        return {"message": "Blog updated succesfully!"}, 201
    except:
        abort(404, message="Blogs not found.")

# delete a blog


@app.route("/blog/delete/<int:id>", methods=["DELETE"])
def delete_blog(id):

    likeObject = db.session.query(Like).filter(
        Like.blog_id == id).all()
    if likeObject:
        for blog in likeObject:
            db.session.delete(blog)

        db.session.commit()
        
    comments = db.session.query(Comment).filter(
        Comment.blog_id == id).all()
    if comments:
        for comment in comments:
            db.session.delete(comment)

        db.session.commit()

    try:

        newBlog = db.session.query(Blog).filter(Blog.id == id).first()
        db.session.delete(newBlog)
        db.session.commit()

        return {"message": "Blog deleted succesfully!"}, 204
    except:
        abort(404, message="Blogs not found.")


# delete a profile


@app.route("/profile/delete/<int:id>", methods=["DELETE"])
def delete_profile(id):
    
    comments=db.session.query(Comment).filter(
        Comment.user_id == id).all()
    
    if comments:
        for comment in comments:
            db.session.delete(comment)
        db.session.commit()    
             
    
    # likes that the user has given
    likeObject = db.session.query(Like).filter(
        Like.user_id == id).all()
    if likeObject:
        for like in likeObject:
            db.session.delete(like)

        db.session.commit()
        
    blogObject = db.session.query(Blog).filter(
        Blog.user_id == id).all()
    if blogObject:
        for blog in blogObject:
            # likes that others have givin to your blogs
            likeObjects = db.session.query(Like).filter(Like.blog_id == blog.id).all()
            for likeObject in likeObjects:
                db.session.delete(likeObject)
                db.session.commit()
                
            comments = db.session.query(Comment).filter(Comment.blog_id == blog.id).all()
            for comment in comments:
                db.session.delete(comment)
                db.session.commit()
            
                
                
            
            
            db.session.delete(blog)
            db.session.commit()

        

    

    user = db.session.query(User).filter(User.id == id).first()
    db.session.delete(user)
    db.session.commit()

    return {"message": "User deleted succesfully!"}, 204
    
        




# like a blog


@app.route("/blog/post/like", methods=["POST"])
def like_blog():

    data = request.get_json()
    data_blog_id = data['blogId']
    data_user_id = data['userId']
    data_like_status = data['likeStatus']

    likeObject = db.session.query(Like).filter(
        Like.blog_id == data_blog_id).filter(Like.user_id == data_user_id).first()

    if likeObject:
        likeObject.like_status = data_like_status
        db.session.add(likeObject)
        db.session.commit()
    else:
        newLikeObject = Like(blog_id=data_blog_id,
                             user_id=data_user_id, like_status=data_like_status)
        db.session.add(newLikeObject)
        db.session.commit()

    return {"message": "Like created succesfully!"}, 201

   # get the likes from a blog


@app.route("/blog/get/likes", methods=["POST", "GET"])
def get_likes_blog():

    data = request.get_json()
    data_blog_id = data['blogId']
    data_user_id = data['userId']

    total_likes = db.session.query(Like).filter(
        Like.blog_id == data_blog_id).filter(Like.like_status == 1).count()

    if not total_likes:
        total_likes = 0

    likeStatus = db.session.query(Like).filter(
        Like.blog_id == data_blog_id).filter(Like.user_id == data_user_id).first()

    if not likeStatus:
        like_status = 0

    else:

        like_status = likeStatus.like_status

    return {"like_status": like_status, "total_likes": total_likes}, 200



# create a comment

@app.route("/comment", methods=["POST"])
def create_comment():
    data = request.get_json()
    comment = Comment(body=data['body'], user_id=data['user_id'],
                blog_id=data['blog_id'])
    db.session.add(comment)
    db.session.commit()

    return {"message": "comment created succesfully!"}, 201



# get all comments for an specific blog



@app.route("/comments/<int:id>", methods=["GET"])
def get_comments(id):
    
    try:

        comments = []
        result = db.session.query(Comment, User).join(
            User).filter(Comment.blog_id == id).order_by(Comment.id).all()

        for comment, user in result:
            comments.append({
                "id":comment.id,
                "body": comment.body,
                "username": user.username,
                "photo": user.photo,
                "blog_id":comment.blog_id
                
            }
            )

        return {"blogs": comments}, 200

    except:
        abort(404, message="Blogs not found.")




# delete a comment


@app.route("/comment/delete/<int:id>", methods=["DELETE"])
def delete_comment(id):

    comment = db.session.query(Comment).filter(Comment.id == id).first()
    
    db.session.delete(comment)
    db.session.commit()
    
    return {"message": "Comment deleted succesfully!"}, 204
   




# @app.route("/changeusername/<int:id>", methods=["PUT"])
# @jwt_required()
# def changeusername(id):

#     jwt = get_jwt()
#     if jwt['sub'] == id:

#         data = request.get_json()
#         user = User.query.get(id)
#         if user:
#             user.username = data["username"]
#             db.session.add(user)
#             db.session.commit()

#             return {"user": user.to_dict()}

#         abort(404, message="User not found.")
#     return {"message": "You are not Authorized"}, 401


# @app.route("/getuser/<int:id>", methods=["GET"])
# def get_user(id):

#     user = User.query.filter(User.id == id).first()
#     if user:
#         return {"user": user.to_dict()}

#     abort(404, message="User not found.")
