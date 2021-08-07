#include <SoftwareSerial.h>
#include <EEPROM.h>


SoftwareSerial mySerial(8, 9); // RX, TX

byte Cambio[4];
byte EdoActual[4];
byte UltimoEdo[4];

byte gbytEdoRele[4];

int gintTrySerial = 0;
int gintTryPrint = 0;
byte message[24];
byte FrameData[6];
int intChecksum;

byte gbytBufferEntrada[255];
int gintContTrama = 0;
bool gbooCompletandoTrama = 0;
int gintDatosProcesado = 0;
int gintBytesEnBuffer = 0;
int gintContLength = 2;
int gintBufferTrama = 0;

String gstrBufferSalida[64];
int gintStringsEnBuffer = 0;
int gintContStrings = 0;
unsigned long glngLastMillisEnviar = 0;
unsigned long glngtimeEnvio = 0;
int gintContEnvio = 0;


unsigned long LastMillis;
unsigned long Intervalo = 50;
String gstrDato = "";
int Sflag = 0;

unsigned long LastSerial;

String gstrBinaryCode = "";
String gstrBinaryCardCode = "";
String gstrHexCardCode = "";
String gstrBuffer = "";

const byte gD0pin = 2;
const byte gD1pin = 3;
unsigned long glngLastTimeDataReceived;
unsigned long glngQuietTime;

unsigned long glngLastMillisD0Received = 0;
unsigned long glngD0Period;
unsigned long glngLastMillisD1Received = 0;
unsigned long glngD1Period;
unsigned long glngAcceptablePeriod = 900;

byte gbytDestino[8];

byte gbytDireccionConstante[8];


void setup() {

  //Serial.begin(9600);
  mySerial.begin(9600);

  pinMode(A0, OUTPUT);
  pinMode(A1, OUTPUT);
  pinMode(A2, OUTPUT);
  pinMode(A3, OUTPUT);
  pinMode(4, INPUT);
  pinMode(5, INPUT);
  pinMode(6, INPUT);
  pinMode(7, INPUT);

  ObtenerDestino();

  LastMillis = millis();
  pinMode(gD0pin, INPUT);
  pinMode(gD1pin, INPUT);
  attachInterrupt(digitalPinToInterrupt(gD0pin), D0Detected, FALLING);
  attachInterrupt(digitalPinToInterrupt(gD1pin), D1Detected, FALLING);


}

void loop() {


  if (gstrBinaryCode.length() > 0) {
    glngQuietTime = abs(millis() - glngLastTimeDataReceived);
    if (glngQuietTime >= 100) {
      gstrBinaryCardCode = gstrBinaryCode;
      gstrBinaryCode = "";
      ProcessCode(gstrBinaryCardCode);
    }
  }

  unsigned long timetoggle = (abs(millis() - LastMillis));    //Parpadeo LED
  if  (timetoggle >= Intervalo) {
    digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
    LastMillis = millis();
  }

  getSerial();

  if (mySerial.available() > 0) {

    getSerial();
    glngLastMillisEnviar = millis();
  }

  glngtimeEnvio = (abs(millis() - glngLastMillisEnviar));
  EnviarBufferSalida();
  entradas();
}

void getSerial() {

  int intAvailable = mySerial.available();
  /*if (intAvailable <= 0) {
    gintTrySerial = 0;
    }*/
  if (intAvailable > 0) {                             //recepcion de datos Serial

    byte bytDatosDisponibles[intAvailable];
    mySerial.readBytes(bytDatosDisponibles, intAvailable); //hck ths

    for (int i = 0 ; i < sizeof(bytDatosDisponibles); i++) {

      if (gbooCompletandoTrama == 1 && gintContLength < 0) {                    //agregar restrw8iccion.
        gbytBufferEntrada[gintBytesEnBuffer] = bytDatosDisponibles[i];
        gintBytesEnBuffer++;
        gintBufferTrama--;
        if (gintBufferTrama == 0) {
          gbooCompletandoTrama = 0;
          gintContLength = 2;
          gintContTrama++;
        }
      }

      if (gbooCompletandoTrama == 1 && gintContLength == 0) {                    //agregar restriccion.
        gbytBufferEntrada[gintBytesEnBuffer] = bytDatosDisponibles[i];
        gintBufferTrama = gbytBufferEntrada[gintBytesEnBuffer] + 1;
        gintBytesEnBuffer++;
        gintContLength--;
      }

      if (gbooCompletandoTrama == 1 && gintContLength > 0) {                    //agregar restriccion.
        gbytBufferEntrada[gintBytesEnBuffer] = bytDatosDisponibles[i];
        gintBytesEnBuffer++;
        gintContLength--;
      }


      if (gbooCompletandoTrama == 0) {
        if (bytDatosDisponibles[i] == 0x7E) {
          gbooCompletandoTrama = 1;
          gbytBufferEntrada[gintBytesEnBuffer] = bytDatosDisponibles[i];
          gintBytesEnBuffer++;
          gintContLength--;
        }
      }


    }

    //Se procesa Si ya hay alguna trama
    while (gintBytesEnBuffer > 0 && gintContTrama >= 1 ) {    //)

      if (gbytBufferEntrada[0] == 0x7E) {
        int intTamano = gbytBufferEntrada[2];
        if (intTamano > 12) {
          byte bytDato[intTamano - 12];
          gstrDato = "";
          for (int i = 0; i < intTamano - 12 ; i++) {
            bytDato[i] = gbytBufferEntrada[15 + i];
            gstrDato += (char)bytDato[i];
          }
          ProcBuffer(gstrDato);
        }
        //Serial.println(gstrDato);
        int aux = gintBytesEnBuffer - (intTamano + 4);
        gintBytesEnBuffer = gintBytesEnBuffer - (intTamano + 4);
        for (int i = 0; i < 255 ; i++) {
          if (i < aux) {
            gbytBufferEntrada[i] = gbytBufferEntrada[i + aux];
          }
          if (i >= aux) gbytBufferEntrada[i] = 0x00;
        }
        gintContTrama--;


      }
    }
    
    //Serial.println(gstrDato);
  }
}


void ObtenerDestino() {
  gbytDestino[0] = EEPROM.read(0);
  gbytDestino[1] = EEPROM.read(1);
  gbytDestino[2] = EEPROM.read(2);
  gbytDestino[3] = EEPROM.read(3);
  gbytDestino[4] = EEPROM.read(4);
  gbytDestino[5] = EEPROM.read(5);
  gbytDestino[6] = EEPROM.read(6);
  gbytDestino[7] = EEPROM.read(7);
}


void entradas() {
  for (int i = 0; i <= 3; i++) {

    EdoActual[i] = digitalRead(i + 4);
    if (UltimoEdo[i] != EdoActual[i]) {
      int intEntrada = i + 1;
      int intEstado = EdoActual[i];
      String strCambio = "{020";
      strCambio += intEntrada;
      strCambio += "0";
      strCambio += intEstado;
      strCambio += "}";


      //Serial.print(strCambio);
      gstrBufferSalida[gintContStrings] = strCambio;
      //Serial.println(gstrBufferSalida[gintStringsEnBuffer]);
      gintStringsEnBuffer++;
      gintContStrings++;
      if (gintContStrings == 63) gintContStrings = 0;

    }
    UltimoEdo[i] = EdoActual[i];
  }
}

void EnviarBufferSalida() {
  if (gintStringsEnBuffer >= 1) {
    //Serial.println(trama);
    //Serial.print(glngtimeEnvio);
    if  (glngtimeEnvio >= 75) {
      Serial.println(gintContEnvio);

      EnviarDatos(gstrBufferSalida[gintContEnvio]);
      gintContEnvio++;
      if (gintContEnvio == 63) gintContEnvio = 0;
      gintStringsEnBuffer--;
      glngLastMillisEnviar = millis();
    }
  }

}


void EnviarDatos(String datos) {

  int suma = 0;
  int len = datos.length() + 14;
  byte lectura[len + 4];
  byte bytDatos[datos.length()];

  datos.getBytes(bytDatos, datos.length() + 1);


  // Header
  lectura[0] = 0x7E;

  // Length
  lectura[1] = 0x00;
  lectura[2] = len;

  lectura[3] = 0x10;
  lectura[4] = 0x01;

  // Dirección destino
  lectura[5] = gbytDestino[0];  //gbytDireccionConstante
  lectura[6] = gbytDestino[1];
  lectura[7] = gbytDestino[2];
  lectura[8] = gbytDestino[3];
  lectura[9] = gbytDestino[4];
  lectura[10] = gbytDestino[5];
  lectura[11] = gbytDestino[6];
  lectura[12] = gbytDestino[7];

  // ----??
  lectura[13] = 0xFF;
  lectura[14] = 0xFE;
  lectura[15] = 0x00;
  lectura[16] = 0x00;

  // Datos
  int aux2 = 0;
  int intLenDatos = sizeof(bytDatos);
  for (int i = 0; i <= intLenDatos - 1; i++) {
    lectura[i + 17] = bytDatos[i];
    aux2 = i + 17;
  }

  // Checksum
  for (int i = 3; i <= aux2; i++) {
    suma += lectura[i];
  }

  intChecksum = 255 - (suma % 256);
  lectura[aux2 + 1] = intChecksum;

  mySerial.write(lectura, sizeof(lectura));

}


void ProcBuffer(String info) {
  String strinfo = "";
  String inst = "";
  int flag = 0;
  for (int i = 0; i <= info.length(); i++) {
    strinfo = info.substring(i - 1, i);
    if (strinfo == "}") {
      flag = 0;
      ProcesarTrama(inst); //aqui imprime el valor entre corchetes
      inst = "";
    }
    if (flag == 1) {
      inst += strinfo;
    }
    if (strinfo == "{") {
      flag = 1;
    }
  }
}

void ProcesarTrama(String orden) {

  //Serial.println(orden);
  String tipo = orden.substring(0, 2);

  if (tipo == "01") {
    String parametro = orden.substring(2, 4);

    if (parametro == "01") {

      String Direccion = orden.substring(4, 20);
      GuardarDireccion(Direccion);
      //Serial.write(direc,sizeof(direc));
    }
    if (parametro == "02") {
      for (int i = 0; i <= 15; i++) {
      }
    }
  }
  if (tipo == "02") {
    String relevador = orden.substring(2, 4);
    String accion = orden.substring(4, 6);
    String tiempo = orden.substring(6, 12);
    //Serial.println(accion);
    if (accion == "00") {
      ApagarRelevador(relevador);
    }
    if (accion == "01") {
      EncenderRelevador(relevador);
    }
    if (accion == "02") {
      // EncenderRelevadorTimer(relevador,tiempo);
    }
  }

  if (tipo == "03") {
    String consulta = orden.substring(2, 4);
    if (consulta == "01") {
      ConsultaEntradas();
    }
    if (consulta == "02") {
      ConsultaRelevadores();
    }
  }


}

void ConsultaEntradas() {
  for (int i = 0; i <= 3; i++) {

    int intEntrada = i + 1;
    int intEstado = EdoActual[i];
    String gstrBuffer = "{030";
    gstrBuffer += intEntrada;
    gstrBuffer += "0";
    gstrBuffer += intEstado;
    gstrBuffer += "}";

    gstrBufferSalida[gintContStrings] = gstrBuffer;
    gintStringsEnBuffer++;
    gintContStrings++;
    if (gintContStrings == 63) gintContStrings = 0;
  }
}

void ConsultaRelevadores() {

  for ( int i = 0; i < 4; i++) {

    int intRelevador = i+1;
    int intEstado = gbytEdoRele[i];

    String gstrBuffer = "{040";
    gstrBuffer += intRelevador;
    gstrBuffer += "0";
    gstrBuffer += intEstado;
    gstrBuffer += "}";

    gstrBufferSalida[gintContStrings] = gstrBuffer;
    gintStringsEnBuffer++;
    gintContStrings++;
    if (gintContStrings == 63) gintContStrings = 0;

  }



}
void GuardarDireccion(String cadena) {

  int intLongit = cadena.length() / 2;
  byte bytDireccion[intLongit];

  for (int i = 0; i <= intLongit - 1; i++) {
    bytDireccion[i] = (HexToDec(cadena.substring(i * 2, (i * 2) + 1)) * 16) + HexToDec(cadena.substring((i * 2) + 1, (i * 2) + 2));
  }

  for (int i = 0; i <= sizeof(bytDireccion) - 1; i++) {
    EEPROM.write(i, bytDireccion[i]);
  }

}

void EncenderRelevador(String rele) {
  Serial.println("encender " + rele);
  if (rele == "01") {
    digitalWrite(A3, HIGH);
    gbytEdoRele[0] = 0x01;
  }
  if (rele == "02") {
    digitalWrite(A2, HIGH);
    gbytEdoRele[1] = 0x01;
  }
  if (rele == "03") {
    digitalWrite(A1, HIGH);
    gbytEdoRele[2] = 0x01;
  }
  if (rele == "04") {
    digitalWrite(A0, HIGH);
    gbytEdoRele[3] = 0x01;
  }
}

void ApagarRelevador(String rele) {
  if (rele == "01") {
    digitalWrite(A3, LOW);
    gbytEdoRele[0] = 0x00;
  }
  if (rele == "02") {
    digitalWrite(A2, LOW);
    gbytEdoRele[1] = 0x00;
  }
  if (rele == "03") {
    digitalWrite(A1, LOW);
    gbytEdoRele[2] = 0x00;
  }
  if (rele == "04") {
    digitalWrite(A0, LOW);
    gbytEdoRele[3] = 0x00;
  }
}

void D0Detected() {
  glngD0Period = abs(micros() - glngLastMillisD0Received);
  glngLastMillisD0Received = micros();
  if (glngD0Period <= glngAcceptablePeriod) {
    return;
  }
  gstrBinaryCode += "0";
  glngLastTimeDataReceived = millis();
}

void D1Detected() {
  glngD1Period = abs(micros() - glngLastMillisD1Received);
  glngLastMillisD1Received = micros();
  if (glngD1Period <= glngAcceptablePeriod) {
    return;
  }
  gstrBinaryCode += "1";
  glngLastTimeDataReceived = millis();
}

void ProcessCode(String BinaryCardCode) {

  //Serial.println(BinaryCardCode);

  if (BinaryCardCode.length() != 26) {
    return;
  }

  gstrHexCardCode = BinaryToHexCardCode(BinaryCardCode);
  //SendCardCode(gstrHexCardCode);

  gstrBuffer = "{01";
  gstrBuffer += gstrHexCardCode;
  gstrBuffer += "}";

  gstrBufferSalida[gintContStrings] = gstrBuffer;
  gintStringsEnBuffer++;
  gintContStrings++;
  if (gintContStrings == 63) gintContStrings = 0;

}


String BinaryToHexCardCode(String strBinary) {

  strBinary = strBinary.substring(1, 25);
  String strHexCardCode = "";
  String strPartial = "";
  String strBit = "";
  int intPartial;

  for (int i = 0; i <= 5; i++) {
    strPartial = strBinary.substring((4 * i), (4 * i) + 4);
    intPartial = 0;

    strBit = strPartial.substring(0, 1); if (strBit == "1") {
      intPartial += 8;
    }
    strBit = strPartial.substring(1, 2); if (strBit == "1") {
      intPartial += 4;
    }
    strBit = strPartial.substring(2, 3); if (strBit == "1") {
      intPartial += 2;
    }
    strBit = strPartial.substring(3, 4); if (strBit == "1") {
      intPartial += 1;
    }

    switch (intPartial) {
      case 0: strHexCardCode += "0"; break;
      case 1: strHexCardCode += "1"; break;
      case 2: strHexCardCode += "2"; break;
      case 3: strHexCardCode += "3"; break;
      case 4: strHexCardCode += "4"; break;
      case 5: strHexCardCode += "5"; break;
      case 6: strHexCardCode += "6"; break;
      case 7: strHexCardCode += "7"; break;
      case 8: strHexCardCode += "8"; break;
      case 9: strHexCardCode += "9"; break;
      case 10: strHexCardCode += "A"; break;
      case 11: strHexCardCode += "B"; break;
      case 12: strHexCardCode += "C"; break;
      case 13: strHexCardCode += "D"; break;
      case 14: strHexCardCode += "E"; break;
      case 15: strHexCardCode += "F"; break;
      default: break;
    }
  }
  return strHexCardCode;
}


int HexToDec(String hex) {
  if (hex == "0") return 0;
  if (hex == "1") return 1;
  if (hex == "2") return 2;
  if (hex == "3") return 3;
  if (hex == "4") return 4;
  if (hex == "5") return 5;
  if (hex == "6") return 6;
  if (hex == "7") return 7;
  if (hex == "8") return 8;
  if (hex == "9") return 9;
  if (hex == "A") return 10;
  if (hex == "B") return 11;
  if (hex == "C") return 12;
  if (hex == "D") return 13;
  if (hex == "E") return 14;
  if (hex == "F") return 15;

}
