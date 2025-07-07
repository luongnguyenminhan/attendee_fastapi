from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.database import get_session
from app.modules.projects.models import Project, ProjectCreate, ProjectRead, ProjectUpdate
from app.modules.users.models import User
from app.utils.security import get_current_user

router = APIRouter()

@router.post("/", response_model=ProjectRead)
async def create_project(
    *, session: Annotated[Session, Depends(get_session)], project: ProjectCreate, current_user: Annotated[User, Depends(get_current_user)]
):
    # For simplicity, associate project with the user's organization. In a real app, you might have more complex logic.
    # Assuming user has an organization_id
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User is not associated with an organization.")

    db_project = Project.model_validate(project, update={"organization_id": current_user.organization_id})
    session.add(db_project)
    session.commit()
    session.refresh(db_project)
    return db_project

@router.get("/", response_model=List[ProjectRead])
async def read_projects(
    *, session: Annotated[Session, Depends(get_session)], current_user: Annotated[User, Depends(get_current_user)]
):
    # Fetch projects belonging to the user's organization
    projects = session.exec(select(Project).where(Project.organization_id == current_user.organization_id)).all()
    return projects

@router.get("/{project_id}", response_model=ProjectRead)
async def read_project(
    *, session: Annotated[Session, Depends(get_session)], project_id: int, current_user: Annotated[User, Depends(get_current_user)]
):
    project = session.exec(select(Project).where(Project.id == project_id, Project.organization_id == current_user.organization_id)).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(
    *, session: Annotated[Session, Depends(get_session)], project_id: int, project: ProjectUpdate, current_user: Annotated[User, Depends(get_current_user)]
):
    db_project = session.exec(select(Project).where(Project.id == project_id, Project.organization_id == current_user.organization_id)).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project_data = project.model_dump(exclude_unset=True)
    db_project.sqlmodel_update(project_data)
    session.add(db_project)
    session.commit()
    session.refresh(db_project)
    return db_project

@router.delete("/{project_id}")
async def delete_project(
    *, session: Annotated[Session, Depends(get_session)], project_id: int, current_user: Annotated[User, Depends(get_current_user)]
):
    project = session.exec(select(Project).where(Project.id == project_id, Project.organization_id == current_user.organization_id)).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    session.delete(project)
    session.commit()
    return {"ok": True}


