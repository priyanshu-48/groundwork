import { useQuery } from "@tanstack/react-query";
import { getMe } from "./api/client";

/** Whether the signed-in user is a visitor of the shared demo workspace (read-only).
 * Only used on pages behind login. The cache is cleared on sign-out, so it never leaks across users. */
export function useIsDemo(): boolean {
  const me = useQuery({
    queryKey: ["me"],
    queryFn: getMe,
    staleTime: 5 * 60_000,
  });
  return me.data?.demo === true;
}
