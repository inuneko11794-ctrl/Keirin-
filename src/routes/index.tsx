import { createFileRoute } from "@tanstack/react-router";
import { Dashboard } from "@/components/keirin/dashboard";

export const Route = createFileRoute("/")({ component: Dashboard });
