import { writable } from 'svelte/store';

export type ToastType = 'success' | 'error' | 'info' | 'warning';

export interface Toast {
	type: ToastType;
	message: string;
	id: number;
	duration: number;
}

export const toasts = writable<Toast[]>([]);

export const addToast = (type: ToastType, message: string, duration = 5000) => {
	const id = Date.now();
	toasts.update((currentToasts) => {
		return [...currentToasts, { type, message, id, duration }];
	});
	setTimeout(() => {
		removeToast(id);
	}, duration);
};

export const removeToast = (id: number) => {
	toasts.update((currentToasts) => {
		return currentToasts.filter((toast) => toast.id !== id);
	});
};
