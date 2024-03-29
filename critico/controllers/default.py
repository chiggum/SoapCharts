# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - api is an example of Hypermedia API support and access control
#########################################################################

INDEX_PAGE='index'
PRODUCT_INDEX_PAGE='product_index'
PRODUCT_PROFILE_PAGE='product_profile'
EDITION_MANAGER_PAGE='edition_manager'
EDITION_PROFILE_PAGE='edition_profile'
SUB_EDITION_PROFILE_PAGE='sub_edition_profile'
CONTRIBUTOR_MANAGER_PAGE='contributor_manager'
CONTRIBUTOR_PROFILE_PAGE='contributor_profile'

import urllib2
import numpy as np
'''
from pprint import pprint
import nltk
import yaml
import sys
import os
import re
'''

MAX_RATING=11
MAX_VOTING=2

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    if not session.auth:
        return userIndex()
    userId = auth.user_id
    userType = getAuthUserType(userId)
    if userType == 'a':
        return userIndex()
    elif userType == 'b':
        return productIndex()


def getNameOfProductAsTR(name_):
    return TR( TD(A(str(name_), _href=URL('default', 'product_index/'+name_))), _class="w2p_fw")

def userIndex():
    form = SQLFORM.factory(Field('product_name', requires=[IS_NOT_EMPTY()]), submit_button='Search', table_name='search_product')
    if not session.auth:
        form.add_button('Login', URL('user/login'))
        form.add_button('Register', URL('user/register'))
    allProductName=getAllProductName()
    if allProductName:
        for name_ in allProductName:
            form[0].insert(-1, getNameOfProductAsTR(name_))
    if form.accepts(request, session):
        redirect(URL(urllib2.quote('product_index/'+form.vars.product_name)))
    return dict(message='Hi user', form=form)

def product_index():
    if request.args(0) == 'chiggypp':
        return getProductPage(getProductIdOf('GameofThrones'))
    if isProductWithThisNameExists(urllib2.unquote(request.args(0))):
        return getProductPage(getProductIdOf(urllib2.unquote(request.args(0))))
    else:
        return dict(message='Product not found!', form=FORM())

def getProductPage(prodId):
    return dict(product_info=getAuthBasedProductProfile(prodId), edition_info=getAuthBasedAllEditonForm(prodId), contrib_info=getAuthBasedAllContributorForm(prodId), news_info=getAuthBasedAllNewsForm(prodId), video_info=getAuthBasedAllVideoForm('product', prodId), review_info=getAuthBasedReviewForm('product', prodId))


def productIndex():
    rows = db(db.product.admin_ref == auth.user_id).select()
    if rows:
        redirect(URL(urllib2.quote(('product_index/'+str(rows[0].name)))))

    form = SQLFORM.factory(submit_button='Update Product Profile', table_name='update_product_profile')
    if form.accepts(request, session):
        prodId = getProductIdOrNewProductId()
        redirect(URL(('product_index/'+str(auth.user_id))))
    return dict(message='Hi Product Admin', form=form)

def product_profile():
    prodId = getProductWithThisAdminId()
    return dict(form=getEditableProductProfile(prodId))

def edition_manager():
    prodId = getProductWithThisAdminId()
    return dict(form=getEditableEditionManager(prodId))

def edition_profile():
    edId = request.vars.ed
    prodId = int(request.vars.prod)

    if edId == '':
        edId = -1
    else:
        edId = int(edId)
        if prodId != getEditionProductId(edId):
            return
    return dict(edition_info=getAuthBasedEditionForm(edId, prodId), sub_edition_info=getAuthBasedAllSubEditonForm(edId), video_info=getAuthBasedAllVideoForm('edition', edId), review_info=getAuthBasedReviewForm('edition', edId), product_name=URL('default', ('index/'+getProductName(prodId))))

def sub_edition_profile():
    edId = int(request.vars.ed)
    subEdId = request.vars.subed

    if subEdId == '':
        subEdId = -1
    else:
        subEdId = int(subEdId)
        if edId != getSubEditionEditionId(subEdId):
            return
    return dict(sub_edition_info=getAuthBasedSubEditionForm(subEdId, edId), video_info=getAuthBasedAllVideoForm('sub_edition', subEdId), review_info=getAuthBasedReviewForm('sub_edition', subEdId), ed_name=URL('default', ('edition_profile?'+'ed='+str(edId)+'&prod='+str(getEditionProductId(edId)))))

def contributor_manager():
    prodId = getProductIdOrNewProductId()
    return dict(form=getContributorManager(prodId))

def contributor_profile():
    contribId = request.vars.contrib
    prodId = getProductIdOrNewProductId()
    if contribId == '':
        contribId = -1
    else:
        contribId = int(contribId)
        if prodId != getContributorProductId(contribId):
            return
    return dict(form=getContributorProfile(contribId, prodId))


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/register_user
    http://..../[app]/default/user/register_product_admin
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    if session.auth and request.args(0) != 'profile' and request.args(0) != 'logout':
        redirect(URL('default', 'index'))
    if request.args(0) == 'register':
        return dict(form=getRegistrationOptionForm())
    elif request.args(0) == 'register_user':
        return dict(form=getUserRegistrationForm())
    elif request.args(0) == 'register_product_admin':
        return dict(form=getProductAdminRegistrationForm())
    elif request.args(0) == 'profile':
        return dict(form=getProfileForm())
    return dict(form=auth())

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_login() 
def api():
    """
    this is example of API with access control
    WEB2PY provides Hypermedia API (Collection+JSON) Experimental
    """
    from gluon.contrib.hypermedia import Collection
    rules = {
        '<table_name>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
        }
    return Collection(db).process(request,response,rules)

'''
User Functions
Start
'''

def selectAuthUser(userId):
    return db(db.auth_user.id == userId).select()

def getAuthUserFirstName(userId):
    rows = selectAuthUser(userId)
    if rows:
        return rows[0].first_name

def getAuthUserLastName(userId):
    rows = selectAuthUser(userId)
    if rows:
        return rows[0].last_name

def getAuthUserUserName(userId):
    rows = selectAuthUser(userId)
    if rows:
        return rows[0].username

def getAuthUserPicBlob(userId):
    rows = selectAuthUser(userId)
    if rows:
        return rows[0].display_picture_blob

def getAuthUserPicName(userId):
    rows = selectAuthUser(userId)
    if rows:
        return rows[0].display_picture_name

def getAuthUserEMail(userId):
    rows = selectAuthUser(userId)
    if rows:
        return rows[0].email

def updateAuthUserUserType(userId, userType):
    db(db.auth_user.id == userId).update(user_type = userType)

def makeAuthUSerUser(userId):
    updateAuthUserUserType(userId, 'a')

def makeAuthUSerSoapAdmin(userId):
    updateAuthUserUserType(userId, 'b')

def approveAuthUser(userId):
    db(db.auth_user.id == userId).update(registration_key='')

def getUserRegistrationForm():
    form = getRegistrationForm()
    if form.accepts(request, session):
        makeAuthUSerUser(form.vars.id)
        approveAuthUser(form.vars.id)
    return form

def getProductAdminRegistrationForm():
    form = getRegistrationForm()
    if form.accepts(request, session):
        makeAuthUSerSoapAdmin(form.vars.id)
        approveAuthUser(form.vars.id)   ## ------------------- This line will be removed in production
    return form

def disalbeAuthFieldReadOrWrite(fieldList):
    for field in fieldList:
        db.auth_user[field].readable = db.auth_user[field].writable = False

def getRegistrationForm():
    disalbeAuthFieldReadOrWrite(['gender', 'date_of_birth', 'country', 'state_', 'city', 'display_picture_name', 'display_picture_blob'])
    return auth.register()

def getRegistrationOptionForm():
    form = SQLFORM.factory(submit_button='Users, Click here!', table_name='reg_form')
    form.add_button('Product Admin, Click Here!', URL('user/register_product_admin'))
    if form.accepts(request, session):
        redirect(URL('user/register_user'))
    return form

@auth.requires_login()
def getProfileForm():
    disalbeAuthFieldReadOrWrite(['username'])
    return auth.profile()

def getAuthUserType(userId):
    return db(db.auth_user.id == userId).select()[0].user_type

'''
User Functions
End
'''

'''
Product Functions
Start
'''
def insertProduct(prodName, picName, picBlob):
    return db.product.insert(name=prodName, display_picture_name=picName, display_picture_blob=picBlob)

def initProduct():
    return db.product.insert()

def selectProduct(prodId):
    return db(db.product.id == prodId).select()

def getAllProductName():
    names = []
    for row in db().select(db.product.name, distinct=True):
        names.append(row.name)
    return names


def updateProductAspectsScore(prodId, aspectsScoreList):
    rows = selectProduct(prodId)
    if rows:
        db(db.product.id == prodId).update(aspects_score=aspectsScoreList)

def addToProductAspectsScore(prodId, aspectsScore):
    rows = selectProduct(prodId)
    if rows:
        scoreList = rows[0].aspects_score
        if len(scoreList) != len(aspectsScore):
            print 'error len not same'
            return
        else:
            for i in range(len(aspectsScore)):
                scoreList[i] += aspectsScore[i]
            updateProductAspectsScore(prodId, scoreList)


def isProductWithThisIdExists(prodId):
    if not selectProduct(prodId):
        return False
    else:
        return True

def isThisIsTheProductAdmin(prodId, userId):
    rows = selectProduct(prodId)
    if rows:
        if rows[0].admin_ref == userId:
            return True
    return False

def getProductIdOf(prodName):
    if isProductWithThisNameExists(prodName):
        return db(db.product.name == prodName).select()[0].id
    else:
        return -1

def isProductWithThisNameExists(prodName):
    if not db(db.product.name == prodName).select():
        return False
    else:
        return True

def getProductName(prodId):
    rows = selectProduct(prodId)
    if rows:
        return rows[0].name

def updateProductName(prodId, name_):
    rows = selectProduct(prodId)
    if rows:
        db(db.product.id == prodId).update(name=name_)

def getProductPicName(prodId):
    rows = selectProduct(prodId)
    if rows:
        return rows[0].display_picture_name

def updateProductPicName(prodId, picName):
    rows = selectProduct(prodId)
    if rows:
        db(db.product.id == prodId).update(display_picture_name=picName)

def getProductPicBlob(prodId):
    rows = selectProduct(prodId)
    if rows:
        return rows[0].display_picture_blob

def updateProductPicBlob(prodId, picBlob):
    rows = selectProduct(prodId)
    if rows:
        db(db.product.id == prodId).update(display_picture_blob=picBlob)


def updateProductPic(prodId, picName, picBlob):
    db(db.product.id == prodId).update(display_picture_name=picName, display_picture_blob=picBlob)

def getProductIdOrNewProductId():
    val = getProductWithThisAdminId()
    if val == -1:
        return initProduct()
    else:
        return val

def getProductWithThisAdminId():
    rows = db(db.product.admin_ref == auth.user_id).select()
    if(not rows):
        return -1
    else:
        return rows[0].id

def getEditableProductProfile(prodId):
    update = db.product(prodId)
    form = SQLFORM(db.product, update, submit_button='Apply Changes', showid=False, upload=URL(r=request,f='download'))
    form[0].insert(-1,getNetRatingOfProductAsTR(prodId))
    if form.accepts(request, session):
        response.flash='submitted'
    return form


def getNetRatingOfProductAsTR(prodId):
    return TR(TD(LABEL('Net Rating'), _class="w2p_fl"), TD(XML('<i>'+str(getProductRating(prodId))+'</i>'), _class="w2p_fw"))

def productRatingProcessing(form):
    if (not session.auth) or auth.user.user_type=='b':
       form.errors.your_rating = 'Only registered users are allowed to rate'

def getNonEditableProductProfile(prodId):
    update = db.product(prodId)
    form = SQLFORM(db.product, update, buttons=[], showid=False , readonly=True, upload=URL(r=request,f='download'))
    form[0].insert(-1,getNetRatingOfProductAsTR(prodId))
    rateForm = SQLFORM.factory(Field('your_rating', type='integer', requires=[IS_INT_IN_RANGE(1,MAX_RATING)], default=getProductRatingByThisUser(prodId)), table_name=('product_'+str(prodId)))
    if rateForm.accepts(request, session, onvalidation=productRatingProcessing):
        insertProductRating(prodId, rateForm.vars.your_rating)
        redirect(URL(args=request.args, vars=request.get_vars, host=True))
    form.append(rateForm)
    return form

def getAuthBasedProductProfile(prodId):
    if isThisIsTheProductAdmin(prodId, auth.user_id):
        return getEditableProductProfile(prodId)
    else:
        return getNonEditableProductProfile(prodId)

def getProductUsersRated(prodId):
    rows = selectProduct(prodId)
    if rows:
        return rows[0].users_rated

def updateProductUsersRatedList(prodId, usersRatedList):
    rows = selectProduct(prodId)
    if rows:
        db(db.product.id == prodId).update(users_rated=usersRatedList)


def getProductUsersRating(prodId):
    rows = selectProduct(prodId)
    if rows:
        return rows[0].users_rating

def updateProductUsersRatingList(prodId, usersRatingList):
    rows = selectProduct(prodId)
    if rows:
        db(db.product.id == prodId).update(users_rating=usersRatingList)

def insertProductRating(prodId, score):
    usersRatedList = getProductUsersRated(prodId)
    usersRatingList = getProductUsersRating(prodId)
    if not usersRatedList:
        usersRatedList=[auth.user_id]
        usersRatingList=[score]
        updateProductUsersRatedList(prodId, usersRatedList)
        updateProductUsersRatingList(prodId, usersRatingList)

    if auth.user_id in usersRatedList:
        ind = usersRatedList.index(auth.user_id)
        usersRatingList[ind] = score
        updateProductUsersRatingList(prodId, usersRatingList)
    else:
        usersRatedList.append(auth.user_id)
        usersRatingList.append(score)
        updateProductUsersRatedList(prodId, usersRatedList)
        updateProductUsersRatingList(prodId, usersRatingList)

def getProductRating(prodId):
    usersRatingList = getProductUsersRating(prodId)
    if not usersRatingList:
        return 0
    return (1.0*sum(usersRatingList))/len(usersRatingList)

def getProductRatingByThisUser(prodId):
    usersRatedList = getProductUsersRated(prodId)
    score = 0
    if (not session.auth) or (not usersRatedList):
        return 0
    if auth.user_id in usersRatedList:
        usersRatingList = getProductUsersRating(prodId)
        ind = usersRatedList.index(auth.user_id)
        score = usersRatingList[ind]
    return score

'''
Product Functions
End
'''

'''
Edition Functions
Start
'''

def insertEdition(prodId, name_, number_, dor, desc, picName, picBlob):
    return db.edition.insert(product_ref=prodId, name=name_, number=number_, date_of_release=dor, description=desc, display_picture_name=picName, display_picture_blob=picBlob)

def initEdition(prodId):
    return db.edition.insert(product_ref=prodId)

def isEditionWithThisIdExists(edId):
    if not db(db.edition.id == edId).select():
        return False
    else:
        return True

def selectEdition(edId):
    return db(db.edition.id == edId).select()

def isThisTheEditionAdmin(edId, userId):
    prodId = getProductWithThisAdminId()
    rows = selectEdition(edId)
    if rows:
        if rows[0].product_ref == prodId:
            return True
    return False

def getEditionProductId(edId):
    rows = selectEdition(edId)
    if rows:
        return rows[0].product_ref

def updateEditionProductId(edId, prodId):
    rows = selectEdition(edId)
    if rows:
        db(db.edition.id == edId).update(product_ref=prodId)

def getEditionName(edId):
    rows = selectEdition(edId)
    if rows:
        return rows[0].name

def updateEditionName(edId, name_):
    rows = selectEdition(edId)
    if rows:
        db(db.edition.id == edId).update(name=name_)

def getEditionNumber(edId):
    rows = selectEdition(edId)
    if rows:
        return rows[0].number_

def updateEditionNumber(edId, num):
    rows = selectEdition(edId)
    if rows:
        db(db.edition.id == edId).update(number_=num)

def getEditionDOR(edId):
    rows = selectEdition(edId)
    if rows:
        return rows[0].date_of_release

def updateEditionDOR(edId, dor):
    rows = selectEdition(edId)
    if rows:
        db(db.edition.id == edId).update(date_of_release=dor)

def getEditionDesc(edId):
    rows = selectEdition(edId)
    if rows:
        return rows[0].description

def updateEditionDesc(edId, desc):
    rows = selectEdition(edId)
    if rows:
        db(db.edition.id == edId).update(description=desc)

def getEditionPicName(edId):
    rows = selectEdition(edId)
    if rows:
        return rows[0].display_picture_name

def updateEditionPicName(edId, name_):
    rows = selectEdition(edId)
    if rows:
        db(db.edition.id == edId).update(display_picture_name=name_)

def getEditionPicBlob(edId):
    rows = selectEdition(edId)
    if rows:
        return rows[0].display_picture_blob

def updateEditionPicBlob(edId, picBlob):
    rows = selectEdition(edId)
    if rows:
        db(db.edition.id == edId).update(display_picture_blob=blob)

## Returns listof  editions if exists else -1
def getEditionsWithThisProductId(prodId):
    rows = db(db.edition.product_ref == prodId).select()
    if(not rows):
        return -1
    else:
        return rows

def getEditableEditionManager(prodId):
    form = SQLFORM.factory(submit_button='Add Edition', table_name='edition_add')
    form.add_button('Back', URL(INDEX_PAGE))
    rows = db(db.edition.product_ref == prodId).select()
    for row in rows:
        str_=('Edit Edition #' + str(row.number_))
        form.add_button(str_, URL(EDITION_PROFILE_PAGE, vars=dict(ed=str(row.id))))
    if form.accepts(request, session):
        redirect(URL(EDITION_PROFILE_PAGE, vars=dict(ed='')))
    return form

def getAuthBasedEditionForm(edId, prodId):
    if isThisIsTheProductAdmin(prodId, auth.user_id):
        return getEditableEditionForm(edId, prodId)
    else:
        return getNonEditableEditionForm(edId, prodId)
    '''  ## for sub editions
    rows = db(db.sub_edition.edition_ref == edId).select()
    for row in rows:
        str_=('Edit Sub Edition #' + str(row.number_))
        form.add_button(str_, URL(SUB_EDITION_PROFILE_PAGE, vars=dict(ed=str(edId), subed=str(row.id))))
    if isEditionWithThisIdExists(edId):
        form.add_button('Add sub edition', URL(SUB_EDITION_PROFILE_PAGE, vars=dict(ed=str(edId), subed='')))
    ## -----
    '''

def getNetRatingOfEditionAsTR(edId):
    return TR(TD(LABEL('Net Rating'), _class="w2p_fl"), TD(XML('<i>'+str(getEditionRating(edId))+'</i>'), _class="w2p_fw"))

def getNonEditableEditionProfile(edId, prodId):
    update = db.edition(edId)
    form = SQLFORM(db.edition, update, showid=False, readonly=True, buttons=[], upload=URL(r=request,f='download'))
    return form

def getNonEditableEditionManager(prodId):
    allEditions = getEditionsWithThisProductId(prodId)
    allEditonForms = []
    for ed in allEditions:
        allEditonForms.append(getNonEditableEditionProfile(ed.id, prodId))
    return allEditonForms



def getLinkToEditionPageAsTR(edId, prodId):
    return TR(TD(LABEL('URL'), _class="w2p_fl"), TD(A(XML('url'), _href=URL(EDITION_PROFILE_PAGE,  vars=dict(ed=str(edId), prod=str(prodId)))), _class="w2p_fw"))

def getEditableEditionForm(edId, prodId):
    update = db.edition(edId)
    submitBtnStr = 'Apply Changes'
    if not update:
        db.edition.product_ref.default = prodId
        submitBtnStr = 'Submit'
    form = SQLFORM(db.edition, update, deletable=True, showid=False, submit_button=submitBtnStr, upload=URL(r=request,f='download'))
    form[0].insert(-1,getLinkToEditionPageAsTR(edId, prodId))
    form[0].insert(-1,getNetRatingOfEditionAsTR(prodId))
    if form.accepts(request, session):
        print 'submitted'
        response.flash="Submitted"
    return form

def getButtonToAddEditon(prodId):
    addForm = getEditableEditionForm(-1, prodId)
    form = SQLFORM.factory(submit_button='Add Edition!', table_name='edition_add')
    if form.accepts(request, session):
        return addForm
    return form


def editionRatingProcessing(form):
    if (not session.auth) or auth.user.user_type=='b':
       form.errors.your_rating = 'Only registered users are allowed to rate'

def getNonEditableEditionForm(edId, prodId):
    update = db.edition(edId)
    form = SQLFORM(db.edition, update, buttons=[], showid=False, readonly=True, upload=URL(r=request,f='download'))
    form[0].insert(-1,getLinkToEditionPageAsTR(edId, prodId))
    form[0].insert(-1,getNetRatingOfEditionAsTR(edId))
    rateForm = SQLFORM.factory(Field('your_rating', requires=[IS_INT_IN_RANGE(1,MAX_RATING)], type='integer', default=getEditionRatingByThisUser(edId)), table_name=('edition_'+str(edId)))
    if rateForm.accepts(request, session, onvalidation=editionRatingProcessing):
        insertEditionRating(edId, rateForm.vars.your_rating)
        redirect(URL(args=request.args, vars=request.get_vars, host=True))
    form.append(rateForm)
    return form

def getAllEditonForms(prodId):
    rows = getEditionsWithThisProductId(prodId)
    if rows == -1:
        return []
    formList = []
    check = isThisIsTheProductAdmin(prodId, auth.user_id)
    for row in rows:
        if check:
            formList.append(getEditableEditionForm(row.id, prodId))
        else:
            formList.append(getNonEditableEditionForm(row.id, prodId))
    return formList

def getAuthBasedButtonToAddEdition(prodId):
    if not isThisIsTheProductAdmin(prodId, auth.user_id):
        return SQLFORM.factory(buttons=[], table_name='edition_null')
    else:
        return getButtonToAddEditon(prodId)

def getAuthBasedAllEditonForm(prodId):
    form = getAuthBasedButtonToAddEdition(prodId)
    allForms = getAllEditonForms(prodId)
    allForms.append(form)
    return allForms

def getEditionUsersRated(edId):
    rows = selectEdition(edId)
    if rows:
        return rows[0].users_rated

def updateEditionUsersRatedList(edId, usersRatedList):
    rows = selectEdition(edId)
    if rows:
        db(db.edition.id == edId).update(users_rated=usersRatedList)

def getEditionUsersRating(edId):
    rows = selectEdition(edId)
    if rows:
        return rows[0].users_rating

def updateEditionUsersRatingList(edId, usersRatingList):
    rows = selectEdition(edId)
    if rows:
        db(db.edition.id == edId).update(users_rating=usersRatingList)

def insertEditionRating(edId, score):
    usersRatedList = getEditionUsersRated(edId)
    usersRatingList = getEditionUsersRating(edId)
    if not usersRatedList:
        usersRatedList=[auth.user_id]
        usersRatingList=[score]
        updateEditionUsersRatedList(edId, usersRatedList)
        updateEditionUsersRatingList(edId, usersRatingList)

    if auth.user_id in usersRatedList:
        ind = usersRatedList.index(auth.user_id)
        usersRatingList[ind] = score
        updateEditionUsersRatingList(edId, usersRatingList)
    else:
        usersRatedList.append(auth.user_id)
        usersRatingList.append(score)
        updateEditionUsersRatedList(edId, usersRatedList)
        updateEditionUsersRatingList(edId, usersRatingList)

def getEditionRating(edId):
    usersRatingList = getEditionUsersRating(edId)
    if not usersRatingList:
        return 0
    return (1.0*sum(usersRatingList))/len(usersRatingList)

def getEditionRatingByThisUser(edId):
    usersRatedList = getEditionUsersRated(edId)
    score = 0
    if (not session.auth) or (not usersRatedList):
        return 0
    if auth.user_id in usersRatedList:
        usersRatingList = getEditionUsersRating(edId)
        ind = usersRatedList.index(auth.user_id)
        score = usersRatingList[ind]
    return score


'''
Edition Functions
End
'''

'''
Sub Edition Functions
Start
'''
def insertSubEdition(prodId, edId, name_, number_, dor, desc, picName, picBlob):
    return db.sub_edition.insert(product_ref=prodId, edition_ref=edId, name=name_, number=number_, date_of_release=dor, description=desc, display_picture_name=picName, display_picture_blob=picBlob)

def initSubEdition(prodId, edId):
    return db.sub_edition.insert(product_ref=prodId, edition_ref=edId)

def isSubEditionWithThisIdExists(subEdId):
    if not db(db.sub_edition.id == subEdId).select():
        return False
    else:
        return True

def selectSubEdition(subEdId):
    return db(db.sub_edition.id == subEdId).select()

def getSubEditionEditionId(subEdId):
    rows = selectSubEdition(subEdId)
    if rows:
        return rows[0].edition_ref

def updateSubEditionEditionId(subEdId, edId):
    rows = selectSubEdition(subEdId)
    if rows:
        db(db.sub_edition.id == subEdId).update(edition_ref=edId)

def getSubEditionProductId(subEdId):
    rows = selectSubEdition(subEdId)
    if rows:
        return rows[0].product_ref

def updateSubEditionProductId(subEdId, prodId):
    rows = selectSubEdition(subEdId)
    if rows:
        db(db.sub_edition.id == subEdId).update(product_ref=prodId)

def getSubEditionName(subEdId):
    rows = selectSubEdition(subEdId)
    if rows:
        return rows[0].name

def updateSubEditionName(subEdId, name_):
    rows = selectSubEdition(subEdId)
    if rows:
        db(db.sub_edition.id == subEdId).update(name=name_)

def getSubEditionNumber(subEdId):
    rows = selectSubEdition(subEdId)
    if rows:
        return rows[0].number_

def updateSubEditionNumber(subEdId, num):
    rows = selectSubEdition(subEdId)
    if rows:
        db(db.sub_edition.id == subEdId).update(number_=num)

def getSubEditionDOR(subEdId):
    rows = selectSubEdition(subEdId)
    if rows:
        return rows[0].date_of_release

def updateSubEditionDOR(subEdId, dor):
    rows = selectSubEdition(subEdId)
    if rows:
        db(db.sub_edition.id == subEdId).update(date_of_release=dor)

def getSubEditionDesc(subEdId):
    rows = selectSubEdition(subEdId)
    if rows:
        return rows[0].description

def updateSubEditionDesc(subEdId, desc):
    rows = selectSubEdition(subEdId)
    if rows:
        db(db.sub_edition.id == subEdId).update(description=desc)

def getSubEditionPicName(subEdId):
    rows = selectSubEdition(subEdId)
    if rows:
        return rows[0].display_picture_name

def updateSubEditionPicName(subEdId, name_):
    rows = selectSubEdition(subEdId)
    if rows:
        db(db.sub_edition.id == subEdId).update(display_picture_name=name_)

def getSubEditionPicBlob(subEdId):
    rows = selectSubEdition(subEdId)
    if rows:
        return rows[0].display_picture_blob

def updateSubEditionPicBlob(subEdId, picBlob):
    rows = selectSubEdition(subEdId)
    if rows:
        db(db.sub_edition.id == subEdId).update(display_picture_blob=blob)

## Returns list of sub editions if exists else -1
def getSubEditionsWithThisEditionId(edId):
    rows = db(db.sub_edition.edition_ref == edId).select()
    if(not rows):
        return -1
    else:
        return rows

def getSubEditionProfile(contribId, edId, prodId):
    update = db.contributor(contribId)
    if not update:
        db.sub_edition.product_ref.default = prodId
        db.sub_edition.edition_ref.default = edId

    form = SQLFORM(db.sub_edition, update, deletable=True, showid=False, submit_button='Apply Changes', upload=URL(r=request,f='download'))
    
    form.add_button('Back', URL(EDITION_PROFILE_PAGE,  vars=dict(ed=str(edId))))

    ## for videos
    '''
    rows = db(db.sub_edition.product_ref == edId).select()
    for row in rows:
        str_=('Edit Sub Edition #' + str(row.number_))
        form.add_button(str_, URL(SUB_EDITION_PROFILE_PAGE, vars=dict(ed=str(edId), subed=str(row.id))))
    if isEditionWithThisIdExists(edId):
        form.add_button('Add sub edition', URL(SUB_EDITION_PROFILE_PAGE, vars=dict(ed=str(edId), subed='')))
    '''
    ## -----
    if form.accepts(request, session):
        if form.deleted:
            redirect(URL(EDITION_PROFILE_PAGE, vars=dict(ed=str(edId))))
        else:
            redirect(URL(SUB_EDITION_PROFILE_PAGE,  vars=dict(subed=str(form.vars.id),ed=str(edId))))
    return form


def getLinkToSubEditionPageAsTR(subEdId, edId):
    return TR(TD(LABEL('URL'), _class="w2p_fl"), TD(A(XML('url'), _href=URL(SUB_EDITION_PROFILE_PAGE, vars=dict(subed=str(subEdId), ed=str(edId))), _class="w2p_fw")))

def getEditableSubEditionForm(subEdId, edId):
    update = db.sub_edition(subEdId)
    submitBtnStr = 'Apply Changes'
    if not update:
        db.sub_edition.edition_ref.default = edId
        submitBtnStr = 'Submit'
    form = SQLFORM(db.sub_edition, update, deletable=True, showid=False, submit_button=submitBtnStr, upload=URL(r=request,f='download'))

    form[0].insert(-1,getLinkToSubEditionPageAsTR(subEdId, edId))
    form[0].insert(-1,getNetRatingOfSubEditionAsTR(subEdId))
    if form.accepts(request, session):
        response.flash="Submitted"
    return form

def getButtonToAddSubEditon(edId):
    addForm = getEditableSubEditionForm(-1, edId)
    form = SQLFORM.factory(submit_button='Add Sub-Edition!', table_name='sub_edition_add')
    if form.accepts(request, session):
        return addForm
    return form

def getNonEditableSubEditionForm(subEdId, edId):
    update = db.sub_edition(subEdId)
    form = SQLFORM(db.sub_edition, update, buttons=[], showid=False, readonly=True, upload=URL(r=request,f='download'))
    form[0].insert(-1,getLinkToSubEditionPageAsTR(subEdId, edId))

    form[0].insert(-1,getNetRatingOfSubEditionAsTR(subEdId))
    rateForm = SQLFORM.factory(Field('your_rating', requires=[IS_INT_IN_RANGE(1,MAX_RATING)], type='integer', default=getSubEditionRatingByThisUser(subEdId)), table_name=('sub_edition_'+str(subEdId)))
    if rateForm.accepts(request, session, onvalidation=subEditionRatingProcessing):
        insertSubEditionRating(subEdId, rateForm.vars.your_rating)
        redirect(URL(args=request.args, vars=request.get_vars, host=True))
    form.append(rateForm)

    return form

def getAllSubEditonForms(edId):
    rows = getSubEditionsWithThisEditionId(edId)
    if rows == -1:
        return []
    formList = []
    check = isThisTheEditionAdmin(edId, auth.user_id)
    for row in rows:
        if check:
            formList.append(getEditableSubEditionForm(row.id, edId))
        else:
            formList.append(getNonEditableSubEditionForm(row.id, edId))
    return formList

def getAuthBasedButtonToAddSubEdition(edId):
    if not isThisTheEditionAdmin(edId, auth.user_id):
        return SQLFORM.factory(buttons=[], table_name='sub_edition_null')
    else:
        return getButtonToAddSubEditon(edId)

def getAuthBasedAllSubEditonForm(prodId):
    form = getAuthBasedButtonToAddSubEdition(prodId)
    allForms = getAllSubEditonForms(prodId)
    allForms.append(form)
    return allForms

def getAuthBasedSubEditionForm(subEdId, edId):
    if isThisTheEditionAdmin(edId, auth.user_id):
        return getEditableSubEditionForm(subEdId, edId)
    else:
        return getNonEditableSubEditionForm(subEdId, edId)



def getNetRatingOfSubEditionAsTR(subEdId):
    return TR(TD(LABEL('Net Rating'), _class="w2p_fl"), TD(XML('<i>'+str(getSubEditionRating(subEdId))+'</i>'), _class="w2p_fw"))


def subEditionRatingProcessing(form):
    if (not session.auth) or auth.user.user_type=='b':
       form.errors.your_rating = 'Only registered users are allowed to rate'

def getSubEditionUsersRated(subEdId):
    rows = selectSubEdition(subEdId)
    if rows:
        return rows[0].users_rated

def updateSubEditionUsersRatedList(subEdId, usersRatedList):
    rows = selectSubEdition(subEdId)
    if rows:
        db(db.sub_edition.id == subEdId).update(users_rated=usersRatedList)

def getSubEditionUsersRating(subEdId):
    rows = selectSubEdition(subEdId)
    if rows:
        return rows[0].users_rating

def updateSubEditionUsersRatingList(subEdId, usersRatingList):
    rows = selectSubEdition(subEdId)
    if rows:
        db(db.sub_edition.id == subEdId).update(users_rating=usersRatingList)

def insertSubEditionRating(subEdId, score):
    usersRatedList = getSubEditionUsersRated(subEdId)
    usersRatingList = getSubEditionUsersRating(subEdId)
    if not usersRatedList:
        usersRatedList=[auth.user_id]
        usersRatingList=[score]
        updateSubEditionUsersRatedList(subEdId, usersRatedList)
        updateSubEditionUsersRatingList(subEdId, usersRatingList)

    if auth.user_id in usersRatedList:
        ind = usersRatedList.index(auth.user_id)
        usersRatingList[ind] = score
        updateSubEditionUsersRatingList(subEdId, usersRatingList)
    else:
        usersRatedList.append(auth.user_id)
        usersRatingList.append(score)
        updateSubEditionUsersRatedList(subEdId, usersRatedList)
        updateSubEditionUsersRatingList(subEdId, usersRatingList)

def getSubEditionRating(subEdId):
    usersRatingList = getSubEditionUsersRating(subEdId)
    if not usersRatingList:
        return 0
    return (1.0*sum(usersRatingList))/len(usersRatingList)

def getSubEditionRatingByThisUser(subEdId):
    usersRatedList = getSubEditionUsersRated(subEdId)
    score = 0
    if (not session.auth) or (not usersRatedList):
        return 0
    if auth.user_id in usersRatedList:
        usersRatingList = getSubEditionUsersRating(subEdId)
        ind = usersRatedList.index(auth.user_id)
        score = usersRatingList[ind]
    return score


'''
Sub Edition Functions
End
'''

'''
Contributor Functions
Start
'''
def insertContributor(prodId, name_1, name_2, role_, url_, picName, picBlob):
    return db.contributor.insert(product_ref=prodId, real_name=name_1, character_name=name_2, role=role_, url=url_, display_picture_name=picName, display_picture_blob=picBlob)

def initContributor(prodId):
    return db.contributor.insert(product_ref=prodId)

def isContributorWithThisIdExists(contribId):
    if not db(db.contributor.id == contribId).select():
        return False
    else:
        return True

def selectContributor(contribId):
    return db(db.contributor.id == contribId).select()

def getContributorProductId(contribId):
    rows = selectContributor(contribId)
    if rows:
        return rows[0].product_ref

def updateContributorProductId(contribId, prodId):
    rows = selectContributor(contribId)
    if rows:
        db(db.contributor.id == contribId).update(product_ref=prodId)

def getContributorRealName(contribId):
    rows = selectContributor(contribId)
    if rows:
        return rows[0].real_name

def updateContributorRealName(contribId, name_):
    rows = selectContributor(contribId)
    if rows:
        db(db.contributor.id == contribId).update(real_name=name_)

def getContributorCharacterName(contribId):
    rows = selectContributor(contribId)
    if rows:
        return rows[0].character_name

def updateContributorCharacterName(contribId, name_):
    rows = selectContributor(contribId)
    if rows:
        db(db.contributor.id == contribId).update(character_name=name_)

def getContributorRole(contribId):
    rows = selectContributor(contribId)
    if rows:
        return rows[0].role

def updateContributorRole(contribId, role_):
    rows = selectContributor(contribId)
    if rows:
        db(db.contributor.id == contribId).update(role=role_)


def getContributorURL(contribId):
    rows = selectContributor(contribId)
    if rows:
        return rows[0].url

def updateContributorURL(contribId, url_):
    rows = selectContributor(contribId)
    if rows:
        db(db.contributor.id == contribId).update(url=url_)

def getContributorPicName(contribId):
    rows = selectContributor(contribId)
    if rows:
        return rows[0].display_picture_name

def updateContributorPicName(contribId, name_):
    rows = selectContributor(contribId)
    if rows:
        db(db.contributor.id == contribId).update(display_picture_name=name_)

def getContributorPicBlob(contribId):
    rows = selectContributor(contribId)
    if rows:
        return rows[0].display_picture_blob

def updateContributorPicBlob(contribId, picBlob):
    rows = selectContributor(contribId)
    if rows:
        db(db.contributor.id == contribId).update(display_picture_blob=blob)

## Returns list of sub editions if exists else -1
def getContributorsWithThisProductId(contribId):
    rows = db(db.contributor.product_ref == contribId).select()
    if(not rows):
        return -1
    else:
        return rows

def getContributorManager(prodId):
    form = SQLFORM.factory(submit_button='Add Contributor', table_name='contributor_add')
    
    form.add_button('Back', URL(INDEX_PAGE))
    rows = db(db.contributor.product_ref == prodId).select()
    
    for row in rows:
        str_=('Edit Contributor Profile: ' + str(row.real_name))
        form.add_button(str_, URL(CONTRIBUTOR_PROFILE_PAGE, vars=dict(contrib=str(row.id))))
    
    if form.accepts(request, session):
        redirect(URL(CONTRIBUTOR_PROFILE_PAGE, vars=dict(contrib='')))
    return form

def getContributorProfile(contribId, prodId):
    update = db.contributor(contribId)
    if not update:
        db.contributor.product_ref.default = prodId
    
    form = SQLFORM(db.contributor, update, deletable=True, showid=False, submit_button='Apply Changes', upload=URL(r=request,f='download'))
    
    form.add_button('Back', URL(CONTRIBUTOR_MANAGER_PAGE))
    
    if form.accepts(request, session):
        if form.deleted:
            redirect(URL(CONTRIBUTOR_MANAGER_PAGE))
        else:
            redirect(URL(CONTRIBUTOR_PROFILE_PAGE,  vars=dict(contrib=str(form.vars.id))))
    return form


def getContributorsWithThisProductId(prodId):
    rows = db(db.contributor.product_ref == prodId).select()
    if(not rows):
        return -1
    else:
        return rows

def getAuthBasedContributorForm(contribId, prodId):
    if isThisIsTheProductAdmin(prodId, auth.user_id):
        return getEditableContributorForm(contribId, prodId)
    else:
        return getNonEditableContributorForm(contribId, prodId)

def getEditableContributorForm(contribId, prodId):
    update = db.contributor(contribId)
    submitBtnStr = 'Apply Changes'
    if not update:
        db.contributor.product_ref.default = prodId
        submitBtnStr = 'Submit'
    form = SQLFORM(db.contributor, update, deletable=True, showid=False, submit_button=submitBtnStr, upload=URL(r=request,f='download'))
    if form.accepts(request, session):
        response.flash="Submitted"
    return form

def getButtonToAddContributor(prodId):
    addForm = getEditableContributorForm(-1, prodId)
    form = SQLFORM.factory(submit_button='Add Contibutor!', table_name='contrib_add')
    if form.accepts(request, session):
        return addForm
    return form

def getNonEditableContributorForm(contribId, prodId):
    update = db.contributor(contribId)
    form = SQLFORM(db.contributor, update, buttons=[], showid=False, readonly=True, upload=URL(r=request,f='download'))
    return form

def getAllContributorForms(prodId):
    rows = getContributorsWithThisProductId(prodId)
    if rows == -1:
        return []
    formList = []
    check = isThisIsTheProductAdmin(prodId, auth.user_id)
    for row in rows:
        if check:
            formList.append(getEditableContributorForm(row.id, prodId))
        else:
            formList.append(getNonEditableContributorForm(row.id, prodId))
    return formList

def getAuthBasedButtonToAddContributor(prodId):
    if not isThisIsTheProductAdmin(prodId, auth.user_id):
        return SQLFORM.factory(buttons=[], table_name='contrib_null')
    else:
        return getButtonToAddContributor(prodId)

def getAuthBasedAllContributorForm(prodId):
    form = getAuthBasedButtonToAddContributor(prodId)
    allForms = getAllContributorForms(prodId)
    allForms.append(form)
    return allForms

'''
Contributor Functions
End
'''

'''
Review Functions
Start
'''
def insertReview(type_, prodId, edId, subEdId, revId, title_, desc):
    db.review.insert(for_type=type_, product_ref=prodId, edition_ref=edId, sub_edition_ref=subEdId, review_ref=revId, title=title_, description=desc)

def initReview(type_, typeId):
    if type_ == 'product':
        return db.review.insert(for_type=type_, product_ref=typeId)
    elif type_ == 'edition':
        return db.review.insert(for_type=type_, edition_ref=typeId)
    elif type_ == 'sub_edition':
        return db.review.insert(for_type=type_, sub_edition_ref=typeId)
    elif type_ == 'reply':
        return db.review.insert(for_type=type_, review_ref=typeId)
    return -1

def selectReview(revId):
    return db(db.review.id == revId).select()

def setReviewAnalyzed(revId):
    rows = selectReview(revId)
    if rows:
        db(db.review.id == revId).update(analyzed=True)

def getNotAnalyzedReviewsOfProduct(prodId):
    eds = getEditionsWithThisProductId(prodId)
    if eds:
        edIdList = [r.id for r in eds]
        subedIdList = []
        for r in edIdList:
            subeds_ = getSubEditionsWithThisEditionId(r)
            if subeds_:
                subeds = [t.id for t in subeds_]
                subedIdList += subeds
    rows = db((db.review.product_ref == prodId or db.review.edition_ref in edIdList or db.review.sub_edition_ref in subedIdList) and db.review.analyzed == False).select()
    if rows:
        revIdList = [r.id for r in rows]
        return revIdList


def isReviewWrittenByThisUser(revId):
    rows = selectReview(revId)
    if rows:
        if rows[0].user_ref == auth.user_id:
            return True
        else:
            return False
    else:
        return True ## TRIVIALLY TRUE BECAUSE REVIEW DOES NOT EXIST

def updateReviewType(revId, type_):
    rows = selectReview(revId)
    if rows and type_ in ['product', 'sub_edition', 'edition', 'reply']:
        db(db.review.id == revId).update(for_type = type_)

def updateReviewProductRef(revId, prodId):
    rows = selectReview(revId)
    if rows:
        db(db.review.id == revId).update(product_ref=prodId)

def updateReviewEditionRef(revId, edId):
    rows = selectReview(revId)
    if rows:
        db(db.review.id == revId).update(edition_ref=edId)

def updateReviewSubEditionRef(revId, subEdId):
    rows = selectReview(revId)
    if rows:
        db(db.review.id == revId).update(sub_edition_ref=subEdId)

def updateReviewReplyRef(revId, repId):
    rows = selectReview(revId)
    if rows:
        db(db.review.id == revId).update(review_ref=repId)

def deleteReview(revId):
    rows = selectReview(revId)
    if rows:
        db(db.review.id == revId).delete()

def updateReviewTypeNTypeId(revId, type_, typeId):
    rows = selectReview(revId)
    if rows:
        updateReviewType(revId, type_)
        if(type_ == 'product'):
            updateReviewProductRef(revId, typeId)
        elif(type_ == 'edition'):
            updateReviewEditionRef(revId, typeId)
        elif(type_ == 'sub_edition'):
            updateReviewSubEditionRef(revId, typeId)
        elif(type_ == 'reply'):
            updateReviewReplyRef(revId, typeId)

def getReviewUserId(revId):
    rows = selectReview(revId)
    if rows:
        return rows[0].user_ref
    else:
        return auth.user_id

def getReviewUserFirstNameAsTR(userId):
    return TR(TD(LABEL('By Firstname: '), _class="w2p_fl"), TD(str(getAuthUserFirstName(userId)), _class="w2p_fw"))

def getReviewUserUserNameAsTR(userId):
    return TR(TD(LABEL('By Username: '), _class="w2p_fl"), TD(str(getAuthUserUserName(userId)),  _class="w2p_fw"))

def getEditableReviewForm(revId, type_, typeId):
    isNewReview = False
    prodId = -1
    update = db.review(revId)
    submitBtnStr = 'Apply Changes'
    if not update:
        isNewReview = True
        if type_ in ['product', 'sub_edition', 'edition', 'reply']:
            db.review.for_type.default = type_
        else:
            return -1
        if(type_ == 'product'):
            db.review.product_ref.default = typeId
            prodId = typeId
        elif(type_ == 'edition'):
            db.review.edition_ref.default = typeId
            prodId = getEditionProductId(typeId)
        elif(type_ == 'sub_edition'):
            db.review.sub_edition_ref.default = typeId
            prodId = getSubEditionEditionId(typeId)
            prodId = getEditionProductId(prodId)
        elif(type_ == 'reply'):
            db.review.reply_ref.default = typeId
        submitBtnStr = 'Submit'

    userId = getReviewUserId(revId)

    form = SQLFORM(db.review, update, submit_button=submitBtnStr, showid=False, deletable=True, upload=URL(r=request,f='download'))
    form[0].insert(-1,getNetUpRatingOfReviewAsTR(revId))
    form[0].insert(-1,getNetDownRatingOfReviewAsTR(revId))
    userName = getReviewUserFirstNameAsTR(userId)
    form[0].insert(-1,userName)

    userName = getReviewUserUserNameAsTR(userId)
    form[0].insert(-1,userName)

    if form.accepts(request, session):
        response.flash = 'Submitted!'
        if isNewReview:
            normScore1 = getSentimentScore(form.vars.description)
            normScore2 = getSentimentScore(form.vars.title)
            addToProductAspectsScore(prodId, normScore1)
            addToProductAspectsScore(prodId, normScore2)
            setReviewAnalyzed(form.vars.id)

    return form

def getNonEditableReviewForm(revId):
    update = db.review(revId)
    form = SQLFORM(db.review, update, buttons=[], showid=False, readonly=True, upload=URL(r=request,f='download'))


    form[0].insert(-1,getNetUpRatingOfReviewAsTR(revId))
    form[0].insert(-1,getNetDownRatingOfReviewAsTR(revId))

    voteDecode = ['neutral', 'up', 'down']

    rateForm = SQLFORM.factory(Field('your_vote', requires=[IS_IN_SET(['up','neutral','down'])], default=voteDecode[getReviewRatingByThisUser(revId)], widget=SQLFORM.widgets.radio.widget), table_name=('review_'+str(revId)))
    if rateForm.accepts(request, session, onvalidation=reviewRatingProcessing):
        vote = rateForm.vars.your_vote
        if vote == 'up':
            vote = 1
        elif vote == 'down':
            vote = -1
        else:
            vote = 0
        insertReviewRating(revId, vote)
        redirect(URL(args=request.args, vars=request.get_vars, host=True))
    form.append(rateForm)

    userId = getReviewUserId(revId)
    userName = getReviewUserFirstNameAsTR(userId)
    form[0].insert(-1,userName)

    userName = getReviewUserUserNameAsTR(userId)
    form[0].insert(-1,userName)

    return form

def getButtonToAddReview(type_, typeId):
    addForm = getEditableReviewForm(-1, type_, typeId)
    form = SQLFORM.factory(submit_button='Write review!', table_name='review_add')
    if form.accepts(request, session):
        return addForm
    return form

def getButtonToEditReview(revId, type_, typeId):
    editForm = getEditableReviewForm(revId, type_, typeId)
    form = SQLFORM.factory(submit_button='Edit review!', table_name='review_add')
    if form.accepts(request, session):
        return editForm
    return form

def getButtonToDeleteReview(revId):
    form = SQLFORM.factory(submit_button='Delete review!', table_name='review_add')
    if form.accepts(request, session):
        deleteReview(revId)
    return form

def getTypeNTypeIdBasedReviews(type_, typeId):
    if(type_ == 'product'):
        return db(db.review.for_type == 'product' and db.review.product_ref == typeId).select()
    elif(type_ == 'edition'):
        return db(db.review.for_type == 'edition' and db.review.edition_ref == typeId).select()
    elif(type_ == 'sub_edition'):
        return db(db.review.for_type == 'sub_edition' and db.review.sub_edition_ref == typeId).select()
    elif(type_ == 'reply'):
        return db(db.review.for_type == 'reply' and db.review.reply_ref == typeId).select()

def getAllReviewForms(type_, typeId):
    rows = getTypeNTypeIdBasedReviews(type_, typeId)
    formList = []
    for row in rows:
        if isReviewWrittenByThisUser(row.id):
            formList.append(getEditableReviewForm(row.id, type_, typeId))
        else:
            formList.append(getNonEditableReviewForm(row.id))
    return formList

def getAuthBasedButtonToAddReview(type_, typeId):
    if not session.auth or auth.user.user_type == 'b':
        return SQLFORM.factory(buttons=[], table_name='review_null')
    else:
        return getButtonToAddReview(type_, typeId)

def getAuthBasedReviewForm(type_, typeId):
    form = getAuthBasedButtonToAddReview(type_, typeId)
    allForms = getAllReviewForms(type_, typeId)
    allForms.append(form)
    return allForms

def getNetUpRatingOfReviewAsTR(revId):
    return TR(TD(LABEL('Net Up votes'), _class="w2p_fl"), TD(XML('<i>'+str(getReviewUpRating(revId))+'</i>'), _class="w2p_fw"))

def getNetDownRatingOfReviewAsTR(revId):
    return TR(TD(LABEL('Net Down votes'), _class="w2p_fl"), TD(XML('<i>'+str(getReviewDownRating(revId))+'</i>'), _class="w2p_fw"))


def reviewRatingProcessing(form):
    if (not session.auth) or auth.user.user_type=='b':
       form.errors.your_vote = 'Only registered users are allowed to rate'

def getReviewUsersRated(revId):
    rows = selectReview(revId)
    if rows:
        return rows[0].users_rated

def updateReviewUsersRatedList(revId, usersRatedList):
    rows = selectReview(revId)
    if rows:
        db(db.review.id == revId).update(users_rated=usersRatedList)

def getReviewUsersRating(revId):
    rows = selectReview(revId)
    if rows:
        return rows[0].users_rating

def updateReviewUsersRatingList(revId, usersRatingList):
    rows = selectReview(revId)
    if rows:
        db(db.review.id == revId).update(users_rating=usersRatingList)

def insertReviewRating(revId, score):
    usersRatedList = getReviewUsersRated(revId)
    usersRatingList = getReviewUsersRating(revId)
    if not usersRatedList:
        usersRatedList=[auth.user_id]
        usersRatingList=[score]
        updateReviewUsersRatedList(revId, usersRatedList)
        updateReviewUsersRatingList(revId, usersRatingList)

    if auth.user_id in usersRatedList:
        ind = usersRatedList.index(auth.user_id)
        usersRatingList[ind] = score
        updateReviewUsersRatingList(revId, usersRatingList)
    else:
        usersRatedList.append(auth.user_id)
        usersRatingList.append(score)
        updateReviewUsersRatedList(revId, usersRatedList)
        updateReviewUsersRatingList(revId, usersRatingList)

def getReviewUpRating(revId):
    usersRatingList = getReviewUsersRating(revId)
    if not usersRatingList:
        return 0
    usersRatingList = np.array(usersRatingList)
    mask = (usersRatingList == 1).astype(int)
    return (1.0*sum(mask))/len(usersRatingList)

def getReviewDownRating(revId):
    usersRatingList = getReviewUsersRating(revId)
    if not usersRatingList:
        return 0
    usersRatingList = np.array(usersRatingList)
    mask = (usersRatingList == -1).astype(int)
    return (1.0*sum(mask))/len(usersRatingList)

def getReviewRatingByThisUser(revId):
    usersRatedList = getReviewUsersRated(revId)
    score = 0
    if (not session.auth) or (not usersRatedList):
        return 0
    if auth.user_id in usersRatedList:
        usersRatingList = getReviewUsersRating(revId)
        ind = usersRatedList.index(auth.user_id)
        score = usersRatingList[ind]
    return score

'''
Review Functions
End
'''


'''
News Functions
Start
'''
def insertNews(prodId, title_, desc, url_, picName, picBlob):
    return db.news.insert(product_ref=prodId, title=title, description=desc, url=url_, display_picture_name=picName, display_picture_blob=picBlob)

def initNews(prodId):
    return db.news.insert(product_ref=prodId)

def isNewsWithThisIdExists(newsId):
    if not db(db.news.id == newsId).select():
        return False
    else:
        return True

def selectNews(newsId):
    return db(db.news.id == newsId).select()

def getNewsProductId(newsId):
    rows = selectNews(newsId)
    if rows:
        return rows[0].product_ref

def updateNewsProductId(newsId, prodId):
    rows = selectNews(newsId)
    if rows:
        db(db.news.id == newsId).update(product_ref=prodId)

def getNewsTitle(newsId):
    rows = selectNews(newsId)
    if rows:
        return rows[0].title

def updateNewsTitle(newsId, title_):
    rows = selectNews(newsId)
    if rows:
        db(db.news.id == newsId).update(title=title_)

def getNewsDescription(newsId):
    rows = selectNews(newsId)
    if rows:
        return rows[0].description

def updateNewsDescription(newsId, desc):
    rows = selectNews(newsId)
    if rows:
        db(db.news.id == newsId).update(description=desc)


def getNewsURL(newsId):
    rows = selectNews(newsId)
    if rows:
        return rows[0].url

def updateNewsURL(newsId, url_):
    rows = selectNews(newsId)
    if rows:
        db(db.news.id == newsId).update(url=url_)

def getNewsPicName(newsId):
    rows = selectNews(newsId)
    if rows:
        return rows[0].display_picture_name

def updateNewsPicName(newsId, name_):
    rows = selectNews(newsId)
    if rows:
        db(db.news.id == newsId).update(display_picture_name=name_)

def getNewsPicBlob(newsId):
    rows = selectNews(newsId)
    if rows:
        return rows[0].display_picture_blob

def updateNewsPicBlob(newsId, picBlob):
    rows = selectNews(newsId)
    if rows:
        db(db.news.id == newsId).update(display_picture_blob=blob)

def getAllNewsWithThisProductId(prodId):
    rows = db(db.news.product_ref == prodId).select()
    if(not rows):
        return -1
    else:
        return rows

def getAuthBasedNewsForm(newsId, prodId):
    if isThisIsTheProductAdmin(prodId, auth.user_id):
        return getEditableNewsForm(newsId, prodId)
    else:
        return getNonEditableNewsForm(newsId, prodId)

def getEditableNewsForm(newsId, prodId):
    update = db.news(newsId)
    submitBtnStr = 'Apply Changes'
    if not update:
        db.news.product_ref.default = prodId
        submitBtnStr = 'Submit'
    form = SQLFORM(db.news, update, deletable=True, showid=False, submit_button=submitBtnStr, upload=URL(r=request,f='download'))
    if form.accepts(request, session):
        response.flash="Submitted"
    return form

def getButtonToAddNews(prodId):
    addForm = getEditableNewsForm(-1, prodId)
    form = SQLFORM.factory(submit_button='Add News!', table_name='news_add')
    if form.accepts(request, session):
        return addForm
    return form

def getNonEditableNewsForm(newsId, prodId):
    update = db.news(newsId)
    form = SQLFORM(db.news, update, buttons=[], showid=False, readonly=True, upload=URL(r=request,f='download'))
    return form

def getAllNewsForms(prodId):
    rows = getAllNewsWithThisProductId(prodId)
    if rows == -1:
        return []
    formList = []
    check = isThisIsTheProductAdmin(prodId, auth.user_id)
    for row in rows:
        if check:
            formList.append(getEditableNewsForm(row.id, prodId))
        else:
            formList.append(getNonEditableNewsForm(row.id, prodId))
    return formList

def getAuthBasedButtonToAddNews(prodId):
    if not isThisIsTheProductAdmin(prodId, auth.user_id):
        return SQLFORM.factory(buttons=[], table_name='news_null')
    else:
        return getButtonToAddNews(prodId)

def getAuthBasedAllNewsForm(prodId):
    form = getAuthBasedButtonToAddNews(prodId)
    allForms = getAllNewsForms(prodId)
    allForms.append(form)
    return allForms
'''
News Functions
End
'''

'''
Video Functions
Start
'''

def insertVideo(prodId, type_, edId, subEdId, name_, url_):
    return db.video.insert(for_type=type_, product_ref=prodId, edition_ref=edId, sub_edition_ref=subEdId, url=url_, name=name_)

def initVideo(type_, typeId, url_):
    if type_ == 'product':
        return db.video.insert(for_type=type_, product_ref=typeId, url=url_)
    elif type_ == 'edition':
        return db.video.insert(for_type=type_, edition_ref=typeId, url=url_)
    elif type_ == 'sub_edition':
        return db.video.insert(for_type=type_, sub_edition_ref=typeId, url=url_)
    return -1

def isVideoWithThisIdExists(videoId):
    if not db(db.video.id == videoId).select():
        return False
    else:
        return True

def selectVideo(videoId):
    return db(db.video.id == videoId).select()

def getVideoProductId(videoId):
    rows = selectVideo(videoId)
    if rows:
        return rows[0].product_ref

def getVideoEditionId(videoId):
    rows = selectVideo(videoId)
    if rows:
        return rows[0].edition_ref

def getVideoSubEditionId(videoId):
    rows = selectVideo(videoId)
    if rows:
        return rows[0].sub_edition_ref

def getVideoName(videoId):
    rows = selectVideo(videoId)
    if rows:
        return rows[0].name

def updateVideoName(videoId, name_):
    rows = selectVideo(videoId)
    if rows:
        db(db.video.id == videoId).update(name=name_)

def getVideoURL(videoId):
    rows = selectVideo(videoId)
    if rows:
        return rows[0].url

def updateVideoURL(videoId, url_):
    rows = selectVideo(videoId)
    if rows:
        db(db.video.id == videoId).update(url=url_)

def getVideoForType(videoId):
    rows = selectVideo(videoId)
    if rows:
        return rows[0].for_type

def isThisTheVideoAdmin(videoId):
    finalId = -1
    type_ = getVideoForType(videoId)
    if type_ == 'product':
        finalId = getVideoProductId(videoId)
    elif type_ == 'edition':
        finalId = getEditionProductId(getVideoEditionId(videoId))
    elif type_ == 'sub_edition':
        finalId = getEditionProductId(getVideoEditionId(getVideoSubEditionId(videoId)))
    return isThisIsTheProductAdmin(finalId, auth.user_id)

def isThisTheVideoAdminUtil(type_, typeId):
    finalId = -1
    if type_ == 'product':
        finalId = typeId
    elif type_ == 'edition':
        finalId = getEditionProductId(typeId)
    elif type_ == 'sub_edition':
        finalId = getSubEditionEditionId(typeId)
        finalId = getEditionProductId(finalId)
    return isThisIsTheProductAdmin(finalId, auth.user_id)

def getAuthBasedVideoForm(videoId):
    if isThisTheVideoAdmin(videoId):
        return getEditableVideoForm(videoId, type_, typeId)
    else:
        return getNonEditableVideoForm(videoId, type_, typeId)

def getEditableVideoForm(videoId, type_, typeId):
    update = db.video(videoId)
    submitBtnStr = 'Apply Changes'
    if not update:
        if type_ in ['product', 'sub_edition', 'edition']:
            db.video.for_type.default = type_
        else:
            return -1
        if(type_ == 'product'):
            db.video.product_ref.default = typeId
        elif(type_ == 'edition'):
            db.video.edition_ref.default = typeId
        elif(type_ == 'sub_edition'):
            db.video.sub_edition_ref.default = typeId
        submitBtnStr = 'Submit'
    form = SQLFORM(db.video, update, deletable=True, showid=False, submit_button=submitBtnStr, upload=URL(r=request,f='download'))
    if form.accepts(request, session):
        response.flash="Submitted"
    return form

def getButtonToAddVideo(type_, typeId):
    addForm = getEditableVideoForm(-1, type_, typeId)
    form = SQLFORM.factory(submit_button='Add Video!', table_name='video_add')
    if form.accepts(request, session):
        return addForm
    return form

def getNonEditableVideoForm(videoId, type_, typeId):
    update = db.video(videoId)
    form = SQLFORM(db.video, update, buttons=[], showid=False, readonly=True, upload=URL(r=request,f='download'))
    return form

def getTypeNTypeIdBasedVideos(type_, typeId):
    if(type_ == 'product'):
        return db(db.video.for_type == 'product' and db.video.product_ref == typeId).select()
    elif(type_ == 'edition'):
        return db(db.video.for_type == 'edition' and db.video.edition_ref == typeId).select()
    elif(type_ == 'sub_edition'):
        return db(db.video.for_type == 'sub_edition' and db.video.sub_edition_ref == typeId).select()
    elif(type_ == 'reply'):
        return db(db.video.for_type == 'reply' and db.video.reply_ref == typeId).select()
    return -1

def getAllVideoForms(type_, typeId):
    rows = getTypeNTypeIdBasedVideos(type_, typeId)
    if rows == -1:
        return []
    formList = []
    if rows:
        check = isThisTheVideoAdmin(rows[0].id)
    for row in rows:
        if check:
            formList.append(getEditableVideoForm(row.id, type_, typeId))
        else:
            formList.append(getNonEditableVideoForm(row.id, type_, typeId))
    return formList

def getAuthBasedButtonToAddVideo(type_, typeId):
    if not isThisTheVideoAdminUtil(type_, typeId):
        return SQLFORM.factory(buttons=[], table_name='video_null')
    else:
        return getButtonToAddVideo(type_, typeId)

def getAuthBasedAllVideoForm(type_, typeId):
    form = getAuthBasedButtonToAddVideo(type_, typeId)
    allForms = getAllVideoForms(type_, typeId)
    allForms.append(form)
    return allForms

'''
Video Functions
End
'''


















'''
Sentiment Analysis Code
Start
'''
'''
class Splitter(object):

    def __init__(self):
        self.nltk_splitter = nltk.data.load('english.pickle')
        self.nltk_tokenizer = nltk.tokenize.TreebankWordTokenizer()

    def split(self, text):
        """
        input format: a paragraph of text
        output format: a list of lists of words.
            e.g.: [['this', 'is', 'a', 'sentence'], ['this', 'is', 'another', 'one']]
        """
        sentences = self.nltk_splitter.tokenize(text)
        tokenized_sentences = [self.nltk_tokenizer.tokenize(sent) for sent in sentences]
        return tokenized_sentences


class POSTagger(object):

    def __init__(self):
        pass
        
    def pos_tag(self, sentences):
        """
        input format: list of lists of words
            e.g.: [['this', 'is', 'a', 'sentence'], ['this', 'is', 'another', 'one']]
        output format: list of lists of tagged tokens. Each tagged tokens has a
        form, a lemma, and a list of tags
            e.g: [[('this', 'this', ['DT']), ('is', 'be', ['VB']), ('a', 'a', ['DT']), ('sentence', 'sentence', ['NN'])],
                    [('this', 'this', ['DT']), ('is', 'be', ['VB']), ('another', 'another', ['DT']), ('one', 'one', ['CARD'])]]
        """

        pos = [nltk.pos_tag(sentence) for sentence in sentences]
        #adapt format
        pos = [[(word, word, [postag]) for (word, postag) in sentence] for sentence in pos]
        return pos

class DictionaryTagger(object):

    def __init__(self, dictionary_paths):
        files = [open(path, 'r') for path in dictionary_paths]
        dictionaries = [yaml.load(dict_file) for dict_file in files]
        map(lambda x: x.close(), files)
        self.dictionary = {}
        self.max_key_size = 0
        for curr_dict in dictionaries:
            for key in curr_dict:
                if key in self.dictionary:
                    self.dictionary[key].extend(curr_dict[key])
                else:
                    self.dictionary[key] = curr_dict[key]
                    self.max_key_size = max(self.max_key_size, len(key))

    def tag(self, postagged_sentences):
        return [self.tag_sentence(sentence) for sentence in postagged_sentences]

    def tag_sentence(self, sentence, tag_with_lemmas=False):
        """
        the result is only one tagging of all the possible ones.
        The resulting tagging is determined by these two priority rules:
            - longest matches have higher priority
            - search is made from left to right
        """
        tag_sentence = []
        N = len(sentence)
        if self.max_key_size == 0:
            self.max_key_size = N
        i = 0
        while (i < N):
            j = min(i + self.max_key_size, N) #avoid overflow
            tagged = False
            while (j > i):
                expression_form = ' '.join([word[0] for word in sentence[i:j]]).lower()
                expression_lemma = ' '.join([word[1] for word in sentence[i:j]]).lower()
                if tag_with_lemmas:
                    literal = expression_lemma
                else:
                    literal = expression_form
                if literal in self.dictionary:
                    
                    is_single_token = j - i == 1
                    original_position = i
                    i = j
                    taggings = [tag for tag in self.dictionary[literal]]
                    tagged_expression = (expression_form, expression_lemma, taggings)
                    if is_single_token: #if the tagged literal is a single token, conserve its previous taggings:
                        original_token_tagging = sentence[original_position][2]
                        tagged_expression[2].extend(original_token_tagging)
                    tag_sentence.append(tagged_expression)
                    tagged = True
                else:
                    j = j - 1
            if not tagged:
                tag_sentence.append(sentence[i])
                i += 1
        return tag_sentence

def value_of(sentiment):
    if sentiment == 'positive': return 1
    if sentiment == 'negative': return -1
    return 0

def sentence_score(sentence_tokens, previous_token, acum_score):    
    if not sentence_tokens:
        return acum_score
    else:
        current_token = sentence_tokens[0]
        tags = current_token[2]
        token_score = sum([value_of(tag) for tag in tags])
        if previous_token is not None:
            previous_tags = previous_token[2]
            if 'inc' in previous_tags:
                token_score *= 2.0
            elif 'dec' in previous_tags:
                token_score /= 2.0
            elif 'inv' in previous_tags:
                token_score *= -1.0
        return sentence_score(sentence_tokens[1:], current_token, acum_score + token_score)

def sentiment_score(review):
    return sum([sentence_score(sentence, None, 0.0) for sentence in review])

aspects = ['comedy', 'action', 'romance', 'drama', 'mystery']
splitter = Splitter()
postagger = POSTagger()
myCwd='/home/dhruv/web2py/applications/critico/controllers'
dicttagger = [DictionaryTagger([ (myCwd + '/dicts/positive_' + r + '.yml'), (myCwd + '/dicts/negative_' + r + '.yml'), myCwd+'/dicts/inc.yml', myCwd+'/dicts/dec.yml', myCwd+'/dicts/inv.yml']) for r in aspects]

def getSentimentScore(text):
    splitted_sentences = splitter.split(text)
    pos_tagged_sentences = postagger.pos_tag(splitted_sentences)
    dict_tagged_sentences_list = [dtagger.tag(pos_tagged_sentences) for dtagger in dicttagger]
    score = [sentiment_score(dict_tagged_sentences) for dict_tagged_sentences in dict_tagged_sentences_list]
    return score
'''

def getSentimentScore(text):
    return [0,0,0,0]