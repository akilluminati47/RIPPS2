/* RIPPS2 build 126: POPSTARTER's IGR pictures in RIPPS2's in-game menu look (igrmenu.c's renderer and font, scale 2) */
#include <stdio.h>
#include <string.h>
#include "igrmenu.c"
static u8 buf[320 * 252 * 3];
static void page(const char *out, int sel)
{
    static igrm_line_t lines[IGRM_LINES];
    int y;
    igrmLine = lines;
    igrmSx = igrmSy = 2;
    igrmBpp = 3;
    igrmLines = 0;
    igrmH = PH;
    igrmSep1 = 14;
    igrmSep2 = 114;
    igrmBarY = sel ? 95 : -100;
    igrmBarH = 17;
    igrmText(4, TEXT_X, C_TITLE, "RIPPS2");
    igrmText(4, PW - TEXT_X - 6 * 10 + 1, C_DIM, "POPSTARTER");
    igrmText(24, TEXT_X, C_TEXT, "QUIT THE GAME?");
    igrmText(44, TEXT_X, C_TEXT, "THE PS1 GAME ENDS HERE");
    igrmText(54, TEXT_X, C_DIM, "POPSTARTER CLOSES IT");
    igrmText(78, TEXT_X, C_WARN, "UNSAVED PROGRESS IS LOST");
    igrmText(100, 47, sel == 1 ? C_SEL : C_ITEM, "YES");
    igrmText(100, 99, sel == 2 ? C_SEL : C_ITEM, "NO");
    igrmText(117, TEXT_X, C_DIM, "\002 ENTER     \001 BACK");
    for (y = 0; y < igrmH * 2; y++)
        igrmRenderLine(buf + y * PW * 2 * 3, y);
    FILE *f = fopen(out, "wb");
    fprintf(f, "P6 320 252 255\n");
    fwrite(buf, 1, sizeof(buf), f);
    fclose(f);
}
int main(void)
{
    page("pops_bg.ppm", 0);
    page("pops_yes.ppm", 1);
    page("pops_no.ppm", 2);
    printf("ok\n");
    return 0;
}
