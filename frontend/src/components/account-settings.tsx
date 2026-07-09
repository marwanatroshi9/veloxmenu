"use client";

import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuthStore } from "@/hooks/use-auth-store";
import { changeEmail, changePassword } from "@/services/auth.service";
import { extractErrorMessage } from "@/lib/api";

const emailSchema = z.object({
  new_email: z.string().email("Enter a valid email"),
  current_password: z.string().min(1, "Password is required"),
});

const passwordSchema = z
  .object({
    current_password: z.string().min(1, "Current password is required"),
    new_password: z.string().min(8, "At least 8 characters"),
    confirm_password: z.string().min(1, "Please confirm your password"),
  })
  .refine((d) => d.new_password === d.confirm_password, {
    message: "Passwords do not match",
    path: ["confirm_password"],
  });

type EmailValues = z.infer<typeof emailSchema>;
type PasswordValues = z.infer<typeof passwordSchema>;

/**
 * Self-service account settings (email + password) for the signed-in user.
 * Role-agnostic — used by both the restaurant dashboard and the admin panel.
 */
export function AccountSettings() {
  const { user, setUser } = useAuthStore();

  const emailForm = useForm<EmailValues>({ resolver: zodResolver(emailSchema) });
  const passwordForm = useForm<PasswordValues>({ resolver: zodResolver(passwordSchema) });

  useEffect(() => {
    if (user) emailForm.setValue("new_email", user.email);
  }, [user, emailForm]);

  async function onChangeEmail(values: EmailValues) {
    try {
      const updated = await changeEmail(values.current_password, values.new_email);
      setUser(updated);
      emailForm.reset({ new_email: updated.email, current_password: "" });
      toast.success("Email updated");
    } catch (err) {
      toast.error(extractErrorMessage(err));
    }
  }

  async function onChangePassword(values: PasswordValues) {
    try {
      await changePassword(values.current_password, values.new_password);
      passwordForm.reset();
      toast.success("Password updated");
    } catch (err) {
      toast.error(extractErrorMessage(err));
    }
  }

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Account</h1>
        <p className="text-muted-foreground">Manage your login email and password.</p>
      </div>

      {/* Change email */}
      <Card>
        <CardHeader>
          <CardTitle>Email address</CardTitle>
          <CardDescription>Used to sign in. Confirm with your current password.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={emailForm.handleSubmit(onChangeEmail)} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="new_email">New email</Label>
              <Input id="new_email" type="email" {...emailForm.register("new_email")} />
              {emailForm.formState.errors.new_email && (
                <p className="text-xs text-destructive">
                  {emailForm.formState.errors.new_email.message}
                </p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="email_current_password">Current password</Label>
              <Input
                id="email_current_password"
                type="password"
                autoComplete="current-password"
                {...emailForm.register("current_password")}
              />
              {emailForm.formState.errors.current_password && (
                <p className="text-xs text-destructive">
                  {emailForm.formState.errors.current_password.message}
                </p>
              )}
            </div>
            <Button type="submit" disabled={emailForm.formState.isSubmitting}>
              {emailForm.formState.isSubmitting && <Loader2 className="h-4 w-4 animate-spin" />}
              Update email
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Change password */}
      <Card>
        <CardHeader>
          <CardTitle>Password</CardTitle>
          <CardDescription>Use at least 8 characters.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={passwordForm.handleSubmit(onChangePassword)} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="current_password">Current password</Label>
              <Input
                id="current_password"
                type="password"
                autoComplete="current-password"
                {...passwordForm.register("current_password")}
              />
              {passwordForm.formState.errors.current_password && (
                <p className="text-xs text-destructive">
                  {passwordForm.formState.errors.current_password.message}
                </p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="new_password">New password</Label>
              <Input
                id="new_password"
                type="password"
                autoComplete="new-password"
                {...passwordForm.register("new_password")}
              />
              {passwordForm.formState.errors.new_password && (
                <p className="text-xs text-destructive">
                  {passwordForm.formState.errors.new_password.message}
                </p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="confirm_password">Confirm new password</Label>
              <Input
                id="confirm_password"
                type="password"
                autoComplete="new-password"
                {...passwordForm.register("confirm_password")}
              />
              {passwordForm.formState.errors.confirm_password && (
                <p className="text-xs text-destructive">
                  {passwordForm.formState.errors.confirm_password.message}
                </p>
              )}
            </div>
            <Button type="submit" disabled={passwordForm.formState.isSubmitting}>
              {passwordForm.formState.isSubmitting && <Loader2 className="h-4 w-4 animate-spin" />}
              Update password
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
