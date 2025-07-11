import { type FC, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { Logout } from "@mui/icons-material";

import { navItems as baseNavItems } from "../../constants";
import { MobileBottomNav } from "./styles";
import { useAppDispatch, useAppSelector } from "../../store/hooks";
import { loggingOutUser, user } from "../../store/reducers/user/userSlice";
import { IconButton } from "../IconButton";
import { isAuthenticated, logout } from "../../store/reducers/user/authSlice";
import { getBio, loggingOutUserBio } from "../../store/reducers/user/bioSlice";
import { loggingOutUserTweets } from "../../store/reducers/tweetSlice";
import { getImageUrl } from "../../utils/getImageUrl";
import { avatarPath } from "../../utils/getAvatarUrlPath";
import { NavItem } from "../app-layout/NavItem";

export const MobileBottom: FC = () => {
  const dispatch = useAppDispatch();
  const currentUser = useAppSelector(user);
  const currentUserBio = useAppSelector(getBio);
  const navigate = useNavigate();
  const isAuth = useAppSelector(isAuthenticated);

  const handleLogout = () => {
    localStorage.removeItem("token");

    dispatch(logout());
    dispatch(loggingOutUser());
    dispatch(loggingOutUserBio());
    dispatch(loggingOutUserTweets());

    navigate("/login", { replace: true });
  };

  const navItems = useMemo(() => {
    const items = [...baseNavItems];

    if (isAuth && currentUser?.id) {
      items.push({
        path: `/main/profile/${currentUser.id}`,
        icon: (
          <IconButton title={`Ir para perfil`}>
            <img
              src={
                currentUserBio?.avatar?.file_path
                  ? getImageUrl(currentUserBio.avatar.file_path)
                  : avatarPath(currentUser.first_name, currentUser.last_name)
              }
              alt={`Avatar de ${currentUser.first_name}`}
              style={{ width: "24px", height: "24px", borderRadius: "50%" }}
            />
          </IconButton>
        ),
        text: "Perfil",
      });
    }

    return items;
  }, [currentUser, currentUserBio, isAuth]);

  return (
    <MobileBottomNav>
      {navItems.map((navItem, index) => (
        <NavItem
          key={`nav-item-${navItem.path}-${index}`}
          to={navItem.path}
          $isActive={
            location.pathname === navItem.path ||
            (navItem.path.startsWith("/") && location.pathname.startsWith(navItem.path) && navItem.path !== "/")
          }
        >
          {navItem.icon} <span>{navItem.text}</span>
        </NavItem>
      ))}

      {isAuth && (
        <div
          onClick={handleLogout}
          style={{ cursor: "pointer" }}
          data-testid="logout-button"
        >
          <NavItem
            to="#"
            $isActive={false}
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              handleLogout();
            }}
          >
            <IconButton title="Logout">
              <Logout />
            </IconButton>
            <span>Sair</span>
          </NavItem>
        </div>
      )}
    </MobileBottomNav>
  );
};
