#include <SD.h> // SD library for reading SD Card
#include <TMRpcm.h> // Arduino library for asynchronous playback of PCM/WAV files
#include <SPI.h> // SPI library for interfacing with SD Card
#define CS_PIN 53 // connect pin 53 of arduino to cs pin of SD Card
#define SPK_PIN 46 //5,6,11 or 46 on Mega, 9 on Uno, Nano, etc

struct Song {
   char  title[50];
   float  sleep_times[50];
   float  low_low[50];
   float  low[50];
   float  high[50];
   float  high_high[50];
};

TMRpcm tmrpcm; // create an object for use in this sketch
int song_index=1;
int num_songs=3;
const int pp=5; // pause-play button pin
const int next=6; // next button pin
const int prev=7; // previous button pin

String line; // pre-define String variables used for reading in text file info
String song_title;
String sleep_times;
String low_low;
String low;
String high;
String high_high; 

void setup()
{ 
 pinMode(pp,INPUT_PULLUP);
 pinMode(next,INPUT_PULLUP);
 pinMode(prev,INPUT_PULLUP);
  
 tmrpcm.speakerPin = SPK_PIN; 
 Serial.begin(9600);
 initializeSD();
 readFile("TEST.TXT");
 
 tmrpcm.setVolume(5); //
 tmrpcm.play("song1.wav"); //the sound file "song" will play each time the arduino powers up, or is reset
                          //try to provide the file name with extension    
 Serial.println("song name: ");
 Serial.println(song_title);  
 Serial.println("sleep times: ");
 Serial.println(sleep_times);
 Serial.println("low_low: ");
 Serial.println(low_low);
 Serial.println("low: ");
 Serial.println(low);     
 Serial.println("high: ");
 Serial.println(high);
 Serial.println("high_high: ");
 Serial.println(high_high);   
}

void loop()
{  
  while(digitalRead(pp)==0 || digitalRead(next)==0 || digitalRead(prev)==0)
  {
    if(digitalRead(pp)==0)
    {
      tmrpcm.pause();
      while(digitalRead(pp)==0);
      delay(200);
    }
    else if(digitalRead(next)==0)
    {
      if(song_index < num_songs)//should be lesser than no. of songs 
      song_index=song_index+1;
      while(digitalRead(next)==0);
      delay(200);
      song();
    }
    else if(digitalRead(prev)==0)
    {
      if(song_index>1)
      song_index=song_index-1;
      while(digitalRead(prev)==0);
      delay(200);
      song();
    }
  }
}

void song (void)
{
  if(song_index==1)
  {
    tmrpcm.play("Song1.wav");  
  }
  else if(song_index==2)
  {
    tmrpcm.play("Song2.wav");  
  }
  else if(song_index==3)
  {
    tmrpcm.play("Song3.wav");  
  }
}

void initializeSD()
{
 Serial.println("Initializing SD card...");
 pinMode(CS_PIN, OUTPUT);
 digitalWrite(CS_PIN, HIGH);
 
 if (SD.begin())
 {
   Serial.println("SD card is ready to use.");
 } else
 {
   Serial.println("SD card initialization failed!");
   return;
 }
}

void readFile(char filename[]){
 File myFile = SD.open(filename);
   if (myFile) {
    // read from the file until there's nothing else in it:
    int file_line = 0;
    while (myFile.available()) {
      line = myFile.readStringUntil('\n'); // one full line of the text file as a String
      if (file_line == 0){
        song_title = line;
      } else if (file_line == 1){
        sleep_times = line;
      } else if (file_line == 2){
        low_low = line;
      } else if (file_line == 3){
        low = line;
      } else if (file_line == 4){
        high = line;
      } else if (file_line == 5){
        high_high = line;
      }
      file_line += 1;
    }
    // close the file:
    myFile.close();
  } else {
    // if the file didn't open, print an error:
    Serial.println("error opening test.txt");
  }
}

//// serial print variable type
//void types(String a) { Serial.println("it's a String"); }
//void types(int a) { Serial.println("it's an int"); }
//void types(char *a) { Serial.println("it's a char*"); }
//void types(float a) { Serial.println("it's a float"); }
//void types(bool a) { Serial.println("it's a bool"); }