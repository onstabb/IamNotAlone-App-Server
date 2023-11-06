from fastapi import APIRouter, HTTPException, status, Query

from contacts import service
from contacts.enums import ContactState, ContactType
from contacts.models import ProfileContact
from contacts.schemas import ContactStateIn, ContactCreateDataIn, ContactOut
from notifications.enums import NotificationType
from notifications.manager import notification_manager
from profiles.dependencies import CurrentActiveProfileByToken, get_active_target_profile, ActiveTargetProfileById


router = APIRouter()


@router.get("/", response_model=list[ContactOut])
def get_contacts(
    current_profile: CurrentActiveProfileByToken, contact_type: ContactType = Query(alias="contactType"),
):

    if contact_type == ContactType.NEW_ESTABLISHED:
        return service.get_new_established_contacts(current_profile)


    return service.get_profile_likes(current_profile)


@router.post("/", response_model=ContactOut, status_code=status.HTTP_201_CREATED)
def create_contact(data_in: ContactCreateDataIn, current_profile: CurrentActiveProfileByToken):

    if data_in.profile_id == current_profile.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You cannot create contact with yourself",
        )
    target_profile = get_active_target_profile(profile_id=data_in.profile_id)
    contact: ProfileContact | None = service.get_contact_by_profile_ids(current_profile.id, target_profile.id)

    if contact:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=f"Contact with profile `{target_profile.id}` already exists"
        )

    contact = service.create_contact_by_initiator(current_profile, target_profile, data_in)
    if data_in.action == ContactState.ESTABLISHED:
        notification_manager.send(
            ContactOut.model_validate(contact, from_attributes=True), target_profile.id, NotificationType.LIKE
        )

    return contact


@router.patch("/{profile_id}", response_model=ContactOut)
def update_contact_state(
        target_profile: ActiveTargetProfileById,
        current_profile: CurrentActiveProfileByToken,
        state_data: ContactStateIn,
):

    contact = service.get_contact_by_profile_ids(current_profile.id, target_profile.id)

    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact doesn't exists")

    if contact.status == ContactState.BLOCKED:
        return contact

    if contact.status and state_data.action != ContactState.BLOCKED:
        return contact

    service.update_contact_status(state_data, current_profile, contact)

    if contact.is_established and current_profile == contact.respondent:
        notification_manager.send(
            ContactOut.model_validate(contact), contact.initiator, NotificationType.CONTACT_ESTABLISHED
        )
    return contact
