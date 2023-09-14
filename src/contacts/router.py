from fastapi import APIRouter, Depends, HTTPException, status

from messages.enums import MessageType
from messages.notificationmanager import notification_manager
from contacts import service
from contacts.enums import ContactState
from contacts.models import ProfileContact
from contacts.schemas import RateIn
from profiles import dependencies as profile_dependencies
from profiles.models import Profile
from profiles.schemas import PublicProfileOut


router = APIRouter(tags=['Contact'], prefix="/contacts")


@router.get("/select", response_model=list[PublicProfileOut])
def select_candidates(profile: Profile = Depends(profile_dependencies.get_active_profile)):
    result = service.get_candidates(profile)
    return result


@router.post("/rate")
async def rate_profile(rate: RateIn, profile: Profile = Depends(profile_dependencies.get_active_profile)):

    other_profile: Profile = profile_dependencies.get_active_profile_by_id(rate.profile_id)
    contact: ProfileContact | None = service.get_contact(profile, other_profile)

    if not contact:
        contact = service.create_contact(initializer=profile, respondent=other_profile)

    if contact.status != ContactState.WAIT:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Contact are already defined")

    profile_state: ContactState = service.get_profile_state(profile, contact)
    if profile_state != ContactState.WAIT:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="The choice has already been made")

    is_initializer = contact.initializer == profile
    service.update_rate(rate, contact, is_initializer)

    if contact.status == ContactState.WAIT and rate.contact == rate.contact.ESTABLISHED:
        notification_manager.create_and_send_message(
            contact.initializer, contact.respondent, MessageType.LIKE, None
        )

    elif contact.is_established:
        notification_manager.create_and_send_message(
            contact.initializer, contact.respondent, MessageType.CONTACT_ESTABLISHED, None
        )
        notification_manager.create_and_send_message(
            contact.respondent, contact.initializer, MessageType.CONTACT_ESTABLISHED, None
        )

    return {"detail": "OK"}
