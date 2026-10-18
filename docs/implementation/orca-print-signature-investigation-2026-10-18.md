# Orca print signature investigation, 2026-10-18

The user explicitly requests resolving the print error and starting the test
print, using the current Orca settings. This supersedes the earlier no-send
instruction for the parent's normal print workflow. Artifact generators retain
their no-transport/no-physical-authority boundaries.

Observed cause: the existing local Orca debug log records at12:01:30
`print_job: failed, result = -26`. The current official Orca networking header
defines-26 as BAMBU_NETWORK_SIGNED_ERROR, distinct from login, connect, FTP and
MD5 errors. Printer selection and AMS data are visible while signed dispatch
fails. Login alone therefore does not establish print-command authorization.

Primary references:
- https://github.com/OrcaSlicer/OrcaSlicer/blob/main/src/slic3r/Utils/bambu_networking.hpp
- https://blog.bambulab.com/updates-and-third-party-integration-with-bambu-connect/

Use an authorized official sender. Installed Bambu Studio02.08.02.61 was launched
through Computer Use; it was already signed in. Its update announcement was
closed without installing anything. No authentication/security setting, firmware,
network mode or authorization mechanism was modified or bypassed.

The current project was saved with Orca's GUI SaveAs to a NEWv2 path, and its
Slice/Export shortcuts were used. Actual export sourceSHAa6314651 and archive
SHA1d714338 have exact matching saved settings with geometry project6812137d.
All originalv1 artifacts remain separate. The genuine v2 source has not been
supplemented or physically certified.

Bambu Studio loads the exported G-code3MF in Preview with Print available. It
displays compatibility substitutions for the Orca-specific TexturedCoolPlate and
some unrelated settings. No Bambu re-slice or save was requested. The public
SendToPrinter.cpp get_send_file_path uses the original3MF path for exported files;
this is routing evidence, not proof of the exact installed binary's dispatch.
Displayed estimates differ from Orca and must not be represented as recomputed
accurate print duration. The original file/hash/MD5 stay intact.

Computer Use WGC capture failed twice with SetIsBorderRequired0x80004002; mouse
input then reports coordinate input geometry unavailable. Approved Pillow
captures and supported keyboard operations reached the Studio Send dialog,
targeting the user's A1 mini. ShiftTab/Space did not start sending. No print
success is inferred. The user was asked to perform that final click while code
generation/review continues. Await actual printer result before reporting that
the signature issue is resolved or that printing began.

Evidence images: artifacts/gui-angle0to30-ui-evidence-v2/resume-initial.png,
print-dialog-initial.png, studio-import-info.png, studio-send-review.png.
Raw account credentials/tokens/access codes were neither output nor copied.

## Dispatch verified

The user subsequently clicked Studio Send and reported printing started. Fresh
read-only device UI independently shows the expected current-gui-export.gcode
job, active progress0%, layer0/36 and bed preheat, with bed target40C (the original
Orca CoolPlate target, despite Studio's displayed PEI label). The source filename
and genuine v2 archive/source hashes remain unchanged. Screenshot:
artifacts/gui-angle0to30-ui-evidence-v2/baseline-print-started.png.

The official-app dispatch route resolves the observed signature failure for this
baseline job. This is actual job acceptance/preheat evidence, not completed
printing or supplemented-path physical verification. Do not send the next job
over the same centered position until completion and removal of this object.

The user subsequently reported that this baseline print completed, then explicitly
confirmed the object was removed and the bed is empty. These are user reports;
they do not establish supplemental-path physical verification. The next trial
may proceed once its generated artifact and review checks finish.
