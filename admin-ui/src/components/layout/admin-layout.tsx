import { component$, Slot } from '@builder.io/qwik';
import { SidebarLayout } from '../ui/sidebar-layout';
import { 
  Sidebar, 
  SidebarHeader, 
  SidebarBody, 
  SidebarSection, 
  SidebarItem, 
  SidebarLabel 
} from '../ui/sidebar';
import { 
  Navbar, 
  NavbarSection, 
  NavbarItem, 
  NavbarSpacer 
} from '../ui/navbar';
import { Avatar } from '../ui/avatar';
import { FaIcon } from '../ui/fa-icon';
import {
  faHome,
  faUsers,
  faBuilding,
  faFolder,
  faRobot,
  faBell,
  faMicrophone,
  faCog,
  faSearch
} from '@fortawesome/free-solid-svg-icons';

export const AdminLayout = component$(() => {
  return (
    <SidebarLayout
      sidebar={
        <Sidebar>
          <SidebarHeader>
            <div class="flex items-center gap-3 px-3 py-2">
              <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600">
                <span class="text-sm font-bold text-white">A</span>
              </div>
              <div>
                <div class="text-sm font-semibold text-white">Attendee Admin</div>
                <div class="text-xs text-gray-300">Management Panel</div>
              </div>
            </div>
          </SidebarHeader>
          <SidebarBody>
            <SidebarSection>
              <SidebarItem href="/">
                <FaIcon icon={faHome} />
                <SidebarLabel>Dashboard</SidebarLabel>
              </SidebarItem>
              
              <SidebarItem href="/users">
                <FaIcon icon={faUsers} />
                <SidebarLabel>Users</SidebarLabel>
              </SidebarItem>
              
              <SidebarItem href="/organizations">
                <FaIcon icon={faBuilding} />
                <SidebarLabel>Organizations</SidebarLabel>
              </SidebarItem>
              
              <SidebarItem href="/projects">
                <FaIcon icon={faFolder} />
                <SidebarLabel>Projects</SidebarLabel>
              </SidebarItem>
              
              <SidebarItem href="/bots">
                <FaIcon icon={faRobot} />
                <SidebarLabel>Bots</SidebarLabel>
              </SidebarItem>
              
              <SidebarItem href="/transcriptions">
                <FaIcon icon={faMicrophone} />
                <SidebarLabel>Transcriptions</SidebarLabel>
              </SidebarItem>
              
              <SidebarItem href="/webhooks">
                <FaIcon icon={faBell} />
                <SidebarLabel>Webhooks</SidebarLabel>
              </SidebarItem>
              
              <SidebarItem href="/settings">
                <FaIcon icon={faCog} />
                <SidebarLabel>Settings</SidebarLabel>
              </SidebarItem>
            </SidebarSection>
          </SidebarBody>
        </Sidebar>
      }
      navbar={
        <Navbar>
          <NavbarSection>
            <NavbarItem>
              <FaIcon icon={faSearch} class="h-4 w-4" />
              <span class="sr-only">Search</span>
            </NavbarItem>
          </NavbarSection>
          
          <NavbarSpacer />
          
          <NavbarSection>
            <NavbarItem>
              <FaIcon icon={faBell} class="h-4 w-4" />
              <span class="sr-only">Notifications</span>
            </NavbarItem>
            
            <NavbarItem>
              <Avatar initials="AD" class="h-8 w-8" />
              <span class="ml-2 text-sm font-medium">Admin</span>
            </NavbarItem>
          </NavbarSection>
        </Navbar>
      }
    >
      <Slot />
    </SidebarLayout>
  );
}); 