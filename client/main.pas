unit main;

interface

uses
  System.SysUtils, System.UIConsts, System.Types, System.UITypes,
  System.Classes,
  System.Variants,
  FMX.Types, FMX.Controls, FMX.Forms, FMX.Graphics, FMX.Dialogs, FMX.Objects,
  FMX.StdCtrls, FMX.Layouts, FMX.Controls.Presentation, FMX.ListBox,
  System.JSON, Winapi.Windows;

type
  TformPrincipal = class(TForm)
    StatusBar1: TStatusBar;
    lyt_menu: TLayout;
    lyt_main: TLayout;
    fundo_main: TRectangle;
    fundo_menu: TRectangle;
    lyt_header: TLayout;
    fundo_header: TRectangle;
    SpeedButton1: TSpeedButton;
    spd_x: TSpeedButton;
    fundo_x: TRectangle;
    Layout1: TLayout;
    Layout2: TLayout;
    Layout9: TLayout;
    listDias: TListBox;
    procedure FormShow(Sender: TObject);
  private
    { Private declarations }
    function SomenteNumeros(const Texto: TDateTime): string;
  public
    { Public declarations }
    procedure CarregaDiasAgenda(limpar: Boolean = False;
      bolinhas: Boolean = False);
  end;

var
  formPrincipal: TformPrincipal;

implementation

{$R *.fmx}

uses frm_dia, dm;

{ TformPrincipal }

procedure TformPrincipal.CarregaDiasAgenda(limpar, bolinhas: Boolean);
var
  Erro: Boolean;
  Itens: TListBoxItem;
  FrameDia: TframeDia;
  size: TSize;
begin
  try
    Erro := False;
    TThread.Synchronize(TThread.CurrentThread,
      procedure
      var
        total: Integer;
      begin
        listDias.BeginUpdate;
        try
          DataModule1.qryDias.Close();
          DataModule1.qryDias.Open();
          DataModule1.qryDias.First;
          while not DataModule1.qryDias.Eof do
          begin

            Itens := TListBoxItem.Create(Self);
            Itens.Selectable := False;
            FrameDia := TframeDia.Create(Self);

            listDias.AddObject(Itens);
            FrameDia.Name := 'Frame_' +
              SomenteNumeros(DataModule1.qryDiasDATA_EVENTO.AsDateTime);
            FrameDia.TagString := 'Frame_' +
              SomenteNumeros(DataModule1.qryDiasDATA_EVENTO.AsDateTime);
            FrameDia.Parent := Itens;
            FrameDia.Align := TAlignLayout.Client;
            FrameDia.Height := listDias.Height;
            Itens.Height := FrameDia.Height+16;
            FrameDia.Margins.Left := 8;
            FrameDia.Margins.Right := 8;
            FrameDia.txt_data.Text :=
              DateToStr(DataModule1.qryDiasDATA_EVENTO.AsDateTime);
            if DateToStr(DataModule1.qryDiasDATA_EVENTO.AsDateTime)
              = DateToStr(now) then
            begin
              FrameDia.txt_data.Text := 'Hoje';
              FrameDia.rect_fundo_data.Fill.Color :=
                StringToAlphaColor('#FF3A9D5D');
            end;

            FrameDia.txt_agendamento_numero.Text :=
              DataModule1.qryDiasQUANTIDADE_EVENTOS.AsString;
            DataModule1.qryDias.Next;
          end;

        finally
          listDias.EndUpdate;
        end;
      end);
  finally
    DataModule1.qryDias.Close;
  end;
end;

procedure TformPrincipal.FormShow(Sender: TObject);
begin
  CarregaDiasAgenda();
end;

function TformPrincipal.SomenteNumeros(const Texto: TDateTime): string;
var
  i: Integer;
begin
  Result := '';
  var
    data: string;
  data := DateTimeToStr(Texto);
  for i := 1 to Length(data) do
    if CharInSet(data[i], ['0' .. '9']) then
      Result := Result + data[i];
end;

end.
