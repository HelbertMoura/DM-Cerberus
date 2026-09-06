# Date, Upload, Notifications, Overlays, Carousel

## Date/time
- date-fns PRIMARY for modular date functions, MIT, official https://date-fns.org.
- Day.js ALTERNATIVE for small immutable-friendly date API, MIT, https://day.js.org.
- Luxon REFERENCE/ALTERNATIVE for explicit zones/Intl, MIT, https://github.com/moment/luxon.
- Temporal REFERENCE/SPECIALIZED for standards-first date/time; evaluate browser/runtime support.

## Upload
- Native input PRIMARY for simple upload.
- react-dropzone ALTERNATIVE for drag/drop, MIT, https://github.com/react-dropzone/react-dropzone.
- Uppy SPECIALIZED for large/multipart/resumable workflows, MIT, https://uppy.io.
- FilePond REFERENCE/ALTERNATIVE for file UI; check maintenance/identity.

Mandatory: client MIME/extension/size checks plus server-side validation, malware controls, storage permissions, signed URL policy and never trusting client names.

## Notifications
- Sonner PRIMARY: MIT, official https://sonner.emilkowal.ski.
- React Hot Toast ALTERNATIVE/REFERENCE: MIT, https://github.com/timolins/react-hot-toast.
- Prefer component-system native if already available. Do not toast errors that require persistent context.

## Overlays
Use existing robust primitives first: Base UI/Radix/Headless UI/React Aria. Require focus trap, focus return, Escape, portal, outside click behavior, nested overlays, scroll lock, screen-reader semantics and mobile full-screen behavior.

## Carousel
- Embla Carousel PRIMARY: MIT, https://www.embla-carousel.com.
- Swiper ALTERNATIVE: MIT, https://swiperjs.com.
- Do not use a carousel when the information hierarchy does not need one.
