import styled from "styled-components";

export const MainContentContainer = styled.main`
  flex-grow: 1;
  width: 80%;
  max-width: 840px;
  border-right: 1px solid ${({ theme }) => theme.colors.border};

  @media (max-width: ${({ theme }) => theme.breakpoints.tablet}) {
    border-right: none;
    max-width: 100%;
  }
`;
