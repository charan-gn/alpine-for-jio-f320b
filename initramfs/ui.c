/*
 * f320b-oss: first light - framebuffer + keypad test for Jio F320B (msm8909)
 * Draws S40-style color bars + status text, cycles on any keypress.
 */
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <linux/fb.h>
#include <linux/input.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <dirent.h>
#include <time.h>

static unsigned short r5(unsigned c){return ((c>>3)&0x1f)<<11;}
static unsigned short g6(unsigned c){return ((c>>2)&0x3f)<<5;}
static unsigned short b5(unsigned c){return ((c>>3)&0x1f);}

/* 8x8 font, chars used by "JIO F320B ALPINE KEY:" */
static const unsigned char font[][8] = {
  [' ']= {0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00},
  ['0']= {0x3C,0x66,0x6E,0x76,0x66,0x66,0x3C,0x00},
  ['2']= {0x3C,0x66,0x06,0x0C,0x30,0x60,0x7E,0x00},
  ['3']= {0x3C,0x66,0x06,0x1C,0x06,0x66,0x3C,0x00},
  ['A']= {0x18,0x3C,0x66,0x66,0x7E,0x66,0x66,0x00},
  ['B']= {0x7C,0x66,0x66,0x7C,0x66,0x66,0x7C,0x00},
  ['E']= {0x7E,0x60,0x60,0x78,0x60,0x60,0x7E,0x00},
  ['F']= {0x7E,0x60,0x60,0x78,0x60,0x60,0x60,0x00},
  ['I']= {0x7E,0x18,0x18,0x18,0x18,0x18,0x7E,0x00},
  ['J']= {0x1E,0x0C,0x0C,0x0C,0x0C,0x6C,0x38,0x00},
  ['K']= {0x66,0x6C,0x78,0x70,0x78,0x6C,0x66,0x00},
  ['L']= {0x60,0x60,0x60,0x60,0x60,0x60,0x7E,0x00},
  ['N']= {0x66,0x76,0x7E,0x7E,0x6E,0x66,0x66,0x00},
  ['O']= {0x3C,0x66,0x66,0x66,0x66,0x66,0x3C,0x00},
  ['P']= {0x7C,0x66,0x66,0x7C,0x60,0x60,0x60,0x00},
  ['Y']= {0x66,0x66,0x66,0x3C,0x18,0x18,0x18,0x00},
  [':']= {0x00,0x18,0x18,0x00,0x00,0x18,0x18,0x00},
};

struct fb { int fd; unsigned short *mem; size_t len; int w,h; };

static void fb_open(struct fb *f){
  f->fd=open("/dev/fb0",O_RDWR);
  if(f->fd<0){perror("fb0");exit(1);}
  struct fb_var_screeninfo v; struct fb_fix_screeninfo fi;
  ioctl(f->fd,FBIOGET_VSCREENINFO,&v);
  ioctl(f->fd,FBIOGET_FSCREENINFO,&fi);
  fprintf(stderr,"fb: %dx%d %dbpp line=%d\n",v.xres,v.yres,v.bits_per_pixel,fi.line_length);
  f->w=v.xres; f->h=v.yres;
  f->len=fi.smem_len;
  f->mem=mmap(0,f->len,PROT_READ|PROT_WRITE,MAP_SHARED,f->fd,0);
  if(f->mem==MAP_FAILED){perror("mmap");exit(1);}
}

static void px(struct fb*f,int x,int y,unsigned c){
  if(x<0||y<0||x>=f->w||y>=f->h)return;
  f->mem[y*(f->w)+x]=r5(c)|g6(c)|b5(c);
}

static void rect(struct fb*f,int x,int y,int w,int h,unsigned c){
  for(int j=0;j<h;j++)for(int i=0;i<w;i++)px(f,x+i,y+j,c);
}

static void text(struct fb*f,const char*s,int tx,int ty,unsigned c){
  while(*s){
    const unsigned char*g=font[(unsigned char)*s];
    for(int j=0;j<8;j++)for(int i=0;i<8;i++)
      if(g[j]&(0x80>>i))px(f,tx+i,ty+j,c);
    s++;tx+=8;
  }
}

/* find first evdev keypad */
static int open_keypad(void){
  DIR*d=opendir("/dev/input");
  struct dirent*e;
  while((e=readdir(d))){
    if(strncmp(e->d_name,"event",5))continue;
    char p[64];snprintf(p,sizeof p,"/dev/input/%s",e->d_name);
    int fd=open(p,O_RDONLY);
    if(fd<0)continue;
    char nm[256]="?";
    ioctl(fd,EVIOCGNAME(sizeof nm),nm);
    fprintf(stderr,"input: %s (%s)\n",p,nm);
    return fd; /* first device wins for now */
  }
  return -1;
}

int main(void){
  struct fb f; fb_open(&f);

  static const unsigned pal[4][3]={
    {0x1f,0x61,0xa9},{0xd1,0x34,0x38},{0x33,0xa0,0x52},{0xf2,0xa9,0x00}
  };
  int frame=0;
  int kp=open_keypad();

  for(;;frame++){
    /* top status strip */
    rect(&f,0,0,f.w,16,pal[frame&3][0]);
    text(&f,"JIO F320B",4,4,0xffffff);

    /* S40-ish color field */
    int bw=f.w/4;
    for(int i=0;i<4;i++)
      rect(&f,i*bw,16,bw,f.h-32,
        pal[(i+frame)&3][0]<<16|pal[(i+frame)&3][1]<<8|pal[(i+frame)&3][2]);

    text(&f,"ALPINE",8,f.h/2,0xffffff);
    text(&f,"KEY:",8,f.h/2+12,0xffffff);

    /* bottom softkey strip */
    rect(&f,0,f.h-16,f.w/2,16,0x303030);
    rect(&f,f.w/2,f.h-16,f.w/2,16,0x303030);

    /* wait for key (non-fatal if none) */
    if(kp>=0){
      struct input_event ev;
      ssize_t n=read(kp,&ev,sizeof ev);
      if(n==(ssize_t)sizeof ev && ev.type==EV_KEY && ev.value==1){
        char buf[24];snprintf(buf,sizeof buf,"KEY:%d",(int)ev.code);
        text(&f,buf,48,f.h/2+12,0xffff00);
      }
    } else {
      /* no input yet - slow blink instead */
      struct timespec t={0,400000000};nanosleep(&t,&t);
    }
  }
  return 0;
}
